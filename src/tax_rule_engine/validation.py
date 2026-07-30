from collections import Counter
from collections.abc import Iterable

from .dependencies import build_dependency_graph, topological_sort
from .exceptions import ConfigurationError, UnknownFilterError
from .models import (
    ConditionDefinition,
    DecisionDefinition,
    FilterDefinition,
    ParameterDefinition,
)
from .operators import SUPPORTED_OPERATORS


def _duplicates(values: Iterable[str]) -> set[str]:
    counts = Counter(values)
    return {value for value, count in counts.items() if count > 1}


def validate_configuration(
    parameters: list[ParameterDefinition],
    filters: list[FilterDefinition],
    conditions: list[ConditionDefinition],
    decisions: list[DecisionDefinition],
    available_columns: set[str] | None = None,
) -> list[str]:
    warnings: list[str] = []

    duplicate_parameters = _duplicates(
        item.parameter_name for item in parameters
    )
    duplicate_filters = _duplicates(item.filter_id for item in filters)
    duplicate_conditions = _duplicates(
        item.condition_id for item in conditions
    )
    duplicate_decisions = _duplicates(
        item.decision_id for item in decisions
    )

    duplicate_groups = {
        "parameters": duplicate_parameters,
        "filters": duplicate_filters,
        "conditions": duplicate_conditions,
        "decisions": duplicate_decisions,
    }

    for group_name, duplicates in duplicate_groups.items():
        if duplicates:
            raise ConfigurationError(
                f"Duplicate {group_name}: {sorted(duplicates)}"
            )

    parameter_names = {item.parameter_name for item in parameters}
    filter_ids = {item.filter_id for item in filters}

    conditions_per_filter = Counter(
        item.filter_id for item in conditions if item.enabled
    )

    for filter_item in filters:
        if filter_item.enabled and conditions_per_filter[filter_item.filter_id] == 0:
            raise ConfigurationError(
                f"Enabled filter {filter_item.filter_id} has no conditions"
            )

    for condition in conditions:
        if not condition.enabled:
            continue

        if condition.filter_id not in filter_ids:
            raise UnknownFilterError(
                f"Condition {condition.condition_id} belongs to unknown "
                f"filter {condition.filter_id}"
            )

        if condition.comparison_operator.upper() not in SUPPORTED_OPERATORS:
            raise ConfigurationError(
                f"Condition {condition.condition_id} uses unsupported "
                f"operator {condition.comparison_operator}"
            )

        if (
            condition.comparison_source_type == "PARAMETER"
            and condition.comparison_value not in parameter_names
        ):
            raise ConfigurationError(
                f"Condition {condition.condition_id} references unknown "
                f"parameter {condition.comparison_value}"
            )

        if (
            available_columns is not None
            and condition.source_type == "COLUMN"
            and condition.source_name not in available_columns
        ):
            raise ConfigurationError(
                f"Condition {condition.condition_id} references missing "
                f"column {condition.source_name}"
            )

    for decision in decisions:
        if decision.enabled and decision.filter_id not in filter_ids:
            raise UnknownFilterError(
                f"Decision {decision.decision_id} references unknown "
                f"filter {decision.filter_id}"
            )

    graph = build_dependency_graph(filters, conditions)
    topological_sort(graph)

    priorities = Counter(
        decision.priority for decision in decisions if decision.enabled
    )
    duplicate_priorities = sorted(
        priority for priority, count in priorities.items()
        if count > 1
    )

    if duplicate_priorities:
        warnings.append(
            "Multiple enabled decisions use the same priority: "
            f"{duplicate_priorities}. Their relative precedence may be unclear."
        )

    return warnings
