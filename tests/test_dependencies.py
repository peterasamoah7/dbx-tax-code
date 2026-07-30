import pytest

from tax_rule_engine.dependencies import topological_sort
from tax_rule_engine.exceptions import CircularDependencyError


def test_topological_sort():
    graph = {
        "A": set(),
        "B": {"A"},
        "C": {"A", "B"},
    }

    result = topological_sort(graph)

    assert result.index("A") < result.index("B")
    assert result.index("B") < result.index("C")


def test_cycle_detection():
    graph = {
        "A": {"B"},
        "B": {"A"},
    }

    with pytest.raises(CircularDependencyError):
        topological_sort(graph)
