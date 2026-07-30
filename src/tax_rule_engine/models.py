from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


DataType = Literal["STRING", "INTEGER", "DECIMAL", "BOOLEAN", "DATE"]
LogicalOperator = Literal["AND", "OR"]
SourceType = Literal["COLUMN", "FILTER"]
ComparisonSourceType = Literal["LITERAL", "PARAMETER"]


class RuleSetDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule_set_id: str
    rule_set_name: str
    version: int = Field(ge=1)
    status: str
    effective_from: date
    effective_to: date | None = None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.effective_to and self.effective_to < self.effective_from:
            raise ValueError("effective_to cannot be before effective_from")
        return self


class ParameterDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule_set_id: str
    parameter_name: str
    parameter_value: str
    data_type: DataType
    description: str | None = None


class FilterDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule_set_id: str
    filter_id: str
    filter_name: str
    description: str | None = None
    logical_operator: LogicalOperator
    enabled: bool = True


class ConditionDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule_set_id: str
    condition_id: str
    filter_id: str
    sequence: int = Field(ge=1)
    source_type: SourceType
    source_name: str
    comparison_operator: str
    comparison_source_type: ComparisonSourceType | None = None
    comparison_value: str | None = None
    data_type: DataType
    enabled: bool = True

    @model_validator(mode="after")
    def validate_comparison_source(self):
        no_value_operators = {"IS_TRUE", "IS_FALSE", "IS_NULL", "IS_NOT_NULL"}

        if self.comparison_operator.upper() in no_value_operators:
            return self

        if self.comparison_source_type is None:
            raise ValueError(
                "comparison_source_type is required for this operator"
            )

        if self.comparison_value is None:
            raise ValueError("comparison_value is required for this operator")

        return self


class DecisionDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule_set_id: str
    decision_id: str
    description: str | None = None
    filter_id: str
    expected_filter_result: bool
    tax_code: str
    result_reason: str
    priority: int
    enabled: bool = True
