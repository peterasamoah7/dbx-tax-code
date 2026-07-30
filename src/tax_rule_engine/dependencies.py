from collections.abc import Iterable

from .exceptions import CircularDependencyError, UnknownFilterError
from .models import ConditionDefinition, FilterDefinition


def build_dependency_graph(
    filters: Iterable[FilterDefinition],
    conditions: Iterable[ConditionDefinition],
) -> dict[str, set[str]]:
    filter_ids = {item.filter_id for item in filters}
    graph = {filter_id: set() for filter_id in filter_ids}

    for condition in conditions:
        if not condition.enabled or condition.source_type != "FILTER":
            continue

        if condition.filter_id not in filter_ids:
            raise UnknownFilterError(
                f"Condition {condition.condition_id} belongs to unknown "
                f"filter {condition.filter_id}"
            )

        if condition.source_name not in filter_ids:
            raise UnknownFilterError(
                f"Condition {condition.condition_id} references unknown "
                f"filter {condition.source_name}"
            )

        graph[condition.filter_id].add(condition.source_name)

    return graph


def topological_sort(graph: dict[str, set[str]]) -> list[str]:
    remaining = {
        node: set(dependencies)
        for node, dependencies in graph.items()
    }

    ordered: list[str] = []

    while remaining:
        ready = sorted(
            node for node, dependencies in remaining.items()
            if not dependencies
        )

        if not ready:
            details = ", ".join(
                f"{node} -> {sorted(dependencies)}"
                for node, dependencies in sorted(remaining.items())
            )
            raise CircularDependencyError(
                f"Circular filter dependency detected: {details}"
            )

        ordered.extend(ready)

        for node in ready:
            del remaining[node]

        for dependencies in remaining.values():
            dependencies.difference_update(ready)

    return ordered
