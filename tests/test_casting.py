from datetime import date
from decimal import Decimal

import pytest

from tax_rule_engine.casting import cast_config_value
from tax_rule_engine.exceptions import ConfigurationError


def test_cast_values():
    assert cast_config_value("abc", "STRING") == "abc"
    assert cast_config_value("10", "INTEGER") == 10
    assert cast_config_value("12.50", "DECIMAL") == Decimal("12.50")
    assert cast_config_value("true", "BOOLEAN") is True
    assert cast_config_value("false", "BOOLEAN") is False
    assert cast_config_value("2026-04-06", "DATE") == date(2026, 4, 6)


def test_invalid_boolean():
    with pytest.raises(ConfigurationError):
        cast_config_value("yes", "BOOLEAN")
