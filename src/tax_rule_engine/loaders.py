from datetime import date
from typing import Any

from .models import (
    ConditionDefinition,
    DecisionDefinition,
    FilterDefinition,
    ParameterDefinition,
    RuleSetDefinition,
)


class DeltaRuleLoader:
    def __init__(self, spark, database: str = "config"):
        self.spark = spark
        self.database = database

    def _table(self, name: str) -> str:
        return f"{self.database}.{name}"

    def load_active_rule_set(
        self,
        rule_set_id: str,
        as_of_date: date,
    ) -> RuleSetDefinition:
        from pyspark.sql import functions as F

        rows = (
            self.spark.table(self._table("tax_rule_sets"))
            .filter(F.col("rule_set_id") == rule_set_id)
            .filter(F.col("status") == "PUBLISHED")
            .filter(F.col("effective_from") <= F.lit(as_of_date))
            .filter(
                F.col("effective_to").isNull()
                | (F.col("effective_to") >= F.lit(as_of_date))
            )
            .orderBy(F.col("version").desc())
            .limit(1)
            .collect()
        )

        if not rows:
            raise ValueError(
                f"No published rule set found for {rule_set_id} "
                f"on {as_of_date}"
            )

        return RuleSetDefinition(**rows[0].asDict())

    def load_parameters(
        self,
        rule_set_id: str,
        version: int,
    ) -> list[ParameterDefinition]:
        return self._load_models(
            "tax_rule_parameters",
            ParameterDefinition,
            rule_set_id,
            version,
        )

    def load_filters(
        self,
        rule_set_id: str,
        version: int,
    ) -> list[FilterDefinition]:
        return self._load_models(
            "tax_filters",
            FilterDefinition,
            rule_set_id,
            version,
        )

    def load_conditions(
        self,
        rule_set_id: str,
        version: int,
    ) -> list[ConditionDefinition]:
        return self._load_models(
            "tax_filter_conditions",
            ConditionDefinition,
            rule_set_id,
            version,
        )

    def load_decisions(
        self,
        rule_set_id: str,
        version: int,
    ) -> list[DecisionDefinition]:
        return self._load_models(
            "tax_decisions",
            DecisionDefinition,
            rule_set_id,
            version,
        )

    def _load_models(
        self,
        table_name: str,
        model_type,
        rule_set_id: str,
        version: int,
    ) -> list[Any]:
        from pyspark.sql import functions as F

        rows = (
            self.spark.table(self._table(table_name))
            .filter(F.col("rule_set_id") == rule_set_id)
            .filter(F.col("version") == version)
            .collect()
        )

        return [
            model_type(
                **{
                    key: value
                    for key, value in row.asDict().items()
                    if key in model_type.model_fields
                }
            )
            for row in rows
        ]
