from collections import defaultdict
from datetime import date
from typing import Any

from .casting import cast_config_value
from .dependencies import build_dependency_graph, topological_sort
from .loaders import DeltaRuleLoader
from .models import (
    ConditionDefinition,
    DecisionDefinition,
    FilterDefinition,
    ParameterDefinition,
)
from .operators import build_spark_comparison, combine_spark_conditions
from .validation import validate_configuration


class TaxRuleEngine:
    def __init__(self, spark, database: str = "config"):
        self.spark = spark
        self.loader = DeltaRuleLoader(spark, database)

    def execute(
        self,
        df,
        rule_set_id: str,
        as_of_date: date,
        keep_filter_columns: bool = True,
    ):
        rule_set = self.loader.load_active_rule_set(
            rule_set_id,
            as_of_date,
        )

        parameters = self.loader.load_parameters(
            rule_set.rule_set_id,
            rule_set.version,
        )
        filters = self.loader.load_filters(
            rule_set.rule_set_id,
            rule_set.version,
        )
        conditions = self.loader.load_conditions(
            rule_set.rule_set_id,
            rule_set.version,
        )
        decisions = self.loader.load_decisions(
            rule_set.rule_set_id,
            rule_set.version,
        )

        warnings = validate_configuration(
            parameters=parameters,
            filters=filters,
            conditions=conditions,
            decisions=decisions,
            available_columns=set(df.columns),
        )

        result_df, calculated_filters = self._apply_filters(
            df,
            parameters,
            filters,
            conditions,
        )

        result_df = self._apply_decisions(
            result_df,
            decisions,
            calculated_filters,
            rule_set.rule_set_id,
            rule_set.version,
            as_of_date,
        )

        if not keep_filter_columns:
            result_df = result_df.drop(
                *[
                    self._filter_column(filter_id)
                    for filter_id in calculated_filters
                ]
            )

        return result_df, warnings

    @staticmethod
    def _filter_column(filter_id: str) -> str:
        return f"_filter_{filter_id}"

    def _apply_filters(
        self,
        df,
        parameters: list[ParameterDefinition],
        filters: list[FilterDefinition],
        conditions: list[ConditionDefinition],
    ):
        parameter_values = {
            item.parameter_name: cast_config_value(
                item.parameter_value,
                item.data_type,
            )
            for item in parameters
        }

        filter_lookup = {
            item.filter_id: item
            for item in filters
            if item.enabled
        }

        conditions_by_filter: dict[str, list[ConditionDefinition]] = (
            defaultdict(list)
        )

        for condition in conditions:
            if condition.enabled:
                conditions_by_filter[condition.filter_id].append(condition)

        for filter_conditions in conditions_by_filter.values():
            filter_conditions.sort(key=lambda item: item.sequence)

        graph = build_dependency_graph(
            filter_lookup.values(),
            [
                condition
                for condition in conditions
                if condition.enabled
            ],
        )
        evaluation_order = topological_sort(graph)

        calculated_filters: set[str] = set()
        result_df = df

        for filter_id in evaluation_order:
            filter_definition = filter_lookup[filter_id]

            expressions = [
                self._build_condition(
                    condition,
                    parameter_values,
                    calculated_filters,
                )
                for condition in conditions_by_filter[filter_id]
            ]

            combined = combine_spark_conditions(
                expressions,
                filter_definition.logical_operator,
            )

            result_df = result_df.withColumn(
                self._filter_column(filter_id),
                combined,
            )
            calculated_filters.add(filter_id)

        return result_df, calculated_filters

    def _build_condition(
        self,
        condition: ConditionDefinition,
        parameter_values: dict[str, Any],
        calculated_filters: set[str],
    ):
        from pyspark.sql import functions as F

        if condition.source_type == "COLUMN":
            source_column = F.col(condition.source_name)
        else:
            if condition.source_name not in calculated_filters:
                raise ValueError(
                    f"Dependent filter {condition.source_name} has not "
                    "been calculated"
                )
            source_column = F.col(
                self._filter_column(condition.source_name)
            )

        value = None

        if condition.comparison_source_type == "LITERAL":
            if condition.comparison_operator.upper() in {"IN", "NOT_IN"}:
                value = [
                    cast_config_value(item.strip(), condition.data_type)
                    for item in (condition.comparison_value or "").split(",")
                    if item.strip()
                ]
            else:
                value = cast_config_value(
                    condition.comparison_value,
                    condition.data_type,
                )

        elif condition.comparison_source_type == "PARAMETER":
            value = parameter_values[condition.comparison_value]

        return build_spark_comparison(
            source_column,
            condition.comparison_operator,
            value,
        )

    def _apply_decisions(
        self,
        df,
        decisions: list[DecisionDefinition],
        calculated_filters: set[str],
        rule_set_id: str,
        version: int,
        as_of_date: date,
    ):
        from pyspark.sql import functions as F

        enabled_decisions = sorted(
            [item for item in decisions if item.enabled],
            key=lambda item: item.priority,
        )

        tax_code_expression = F.lit("REVIEW")
        reason_expression = F.lit("No configured tax rule matched")
        matched_decision_expression = F.lit(None).cast("string")
        matched_priority_expression = F.lit(None).cast("integer")

        for decision in enabled_decisions:
            if decision.filter_id not in calculated_filters:
                raise ValueError(
                    f"Decision {decision.decision_id} references "
                    f"uncalculated filter {decision.filter_id}"
                )

            condition = (
                F.col(self._filter_column(decision.filter_id))
                == F.lit(decision.expected_filter_result)
            )

            tax_code_expression = F.when(
                condition,
                F.lit(decision.tax_code),
            ).otherwise(tax_code_expression)

            reason_expression = F.when(
                condition,
                F.lit(decision.result_reason),
            ).otherwise(reason_expression)

            matched_decision_expression = F.when(
                condition,
                F.lit(decision.decision_id),
            ).otherwise(matched_decision_expression)

            matched_priority_expression = F.when(
                condition,
                F.lit(decision.priority),
            ).otherwise(matched_priority_expression)

        return (
            df
            .withColumn("tax_code", tax_code_expression)
            .withColumn("tax_code_reason", reason_expression)
            .withColumn(
                "matched_decision_id",
                matched_decision_expression,
            )
            .withColumn(
                "matched_decision_priority",
                matched_priority_expression,
            )
            .withColumn("rule_set_id", F.lit(rule_set_id))
            .withColumn("rule_set_version", F.lit(version))
            .withColumn("rule_as_of_date", F.lit(as_of_date))
            .withColumn(
                "rule_evaluated_at",
                F.current_timestamp(),
            )
        )
