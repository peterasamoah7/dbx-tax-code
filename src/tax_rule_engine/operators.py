from typing import Any

from .exceptions import UnsupportedOperatorError


SUPPORTED_OPERATORS = {
    "EQUALS",
    "NOT_EQUALS",
    "GREATER_THAN",
    "GREATER_THAN_OR_EQUAL",
    "LESS_THAN",
    "LESS_THAN_OR_EQUAL",
    "IN",
    "NOT_IN",
    "CONTAINS",
    "STARTS_WITH",
    "ENDS_WITH",
    "IS_TRUE",
    "IS_FALSE",
    "IS_NULL",
    "IS_NOT_NULL",
}


def build_spark_comparison(column, operator: str, value: Any = None):
    """Build a PySpark Column expression.

    Importing pyspark happens inside the function so the rest of the package
    can be unit-tested without Spark installed.
    """
    from pyspark.sql import functions as F

    op = operator.upper()

    if op not in SUPPORTED_OPERATORS:
        raise UnsupportedOperatorError(f"Unsupported operator: {operator}")

    operations = {
        "EQUALS": lambda: column == F.lit(value),
        "NOT_EQUALS": lambda: column != F.lit(value),
        "GREATER_THAN": lambda: column > F.lit(value),
        "GREATER_THAN_OR_EQUAL": lambda: column >= F.lit(value),
        "LESS_THAN": lambda: column < F.lit(value),
        "LESS_THAN_OR_EQUAL": lambda: column <= F.lit(value),
        "IN": lambda: column.isin(value),
        "NOT_IN": lambda: ~column.isin(value),
        "CONTAINS": lambda: column.contains(value),
        "STARTS_WITH": lambda: column.startswith(value),
        "ENDS_WITH": lambda: column.endswith(value),
        "IS_TRUE": lambda: column == F.lit(True),
        "IS_FALSE": lambda: column == F.lit(False),
        "IS_NULL": lambda: column.isNull(),
        "IS_NOT_NULL": lambda: column.isNotNull(),
    }

    return F.coalesce(operations[op](), F.lit(False))


def combine_spark_conditions(expressions: list, logical_operator: str):
    from pyspark.sql import functions as F

    if not expressions:
        raise ValueError("A filter must have at least one condition")

    op = logical_operator.upper()

    if op == "AND":
        result = F.lit(True)
        for expression in expressions:
            result = result & expression
        return result

    if op == "OR":
        result = F.lit(False)
        for expression in expressions:
            result = result | expression
        return result

    raise ValueError(f"Unsupported logical operator: {logical_operator}")
