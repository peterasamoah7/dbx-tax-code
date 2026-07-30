import pytest

from tax_rule_engine.exceptions import ConfigurationError
from tax_rule_engine.models import (
    ConditionDefinition,
    DecisionDefinition,
    FilterDefinition,
    ParameterDefinition,
)
from tax_rule_engine.validation import validate_configuration


def build_valid_configuration():
    parameters = [
        ParameterDefinition(
            rule_set_id="R",
            parameter_name="allowance",
            parameter_value="12570",
            data_type="DECIMAL",
        )
    ]

    filters = [
        FilterDefinition(
            rule_set_id="R",
            filter_id="F1",
            filter_name="Income Check",
            logical_operator="AND",
        )
    ]

    conditions = [
        ConditionDefinition(
            rule_set_id="R",
            condition_id="C1",
            filter_id="F1",
            sequence=1,
            source_type="COLUMN",
            source_name="annual_income",
            comparison_operator="GREATER_THAN",
            comparison_source_type="PARAMETER",
            comparison_value="allowance",
            data_type="DECIMAL",
        )
    ]

    decisions = [
        DecisionDefinition(
            rule_set_id="R",
            decision_id="D1",
            filter_id="F1",
            expected_filter_result=True,
            tax_code="A",
            result_reason="Matched",
            priority=100,
        )
    ]

    return parameters, filters, conditions, decisions


def test_valid_configuration():
    parameters, filters, conditions, decisions = build_valid_configuration()

    warnings = validate_configuration(
        parameters,
        filters,
        conditions,
        decisions,
        available_columns={"annual_income"},
    )

    assert warnings == []


def test_missing_column():
    parameters, filters, conditions, decisions = build_valid_configuration()

    with pytest.raises(ConfigurationError):
        validate_configuration(
            parameters,
            filters,
            conditions,
            decisions,
            available_columns={"other_column"},
        )
