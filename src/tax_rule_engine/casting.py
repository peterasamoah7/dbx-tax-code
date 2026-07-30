from datetime import date
from decimal import Decimal
from typing import Any

from .exceptions import ConfigurationError


def cast_config_value(value: str | None, data_type: str) -> Any:
    if value is None:
        return None

    normalised_type = data_type.upper()

    try:
        if normalised_type == "STRING":
            return value

        if normalised_type == "INTEGER":
            return int(value)

        if normalised_type == "DECIMAL":
            return Decimal(value)

        if normalised_type == "BOOLEAN":
            lower_value = value.strip().lower()

            if lower_value not in {"true", "false"}:
                raise ValueError("Boolean values must be true or false")

            return lower_value == "true"

        if normalised_type == "DATE":
            return date.fromisoformat(value)

    except (ValueError, TypeError) as exc:
        raise ConfigurationError(
            f"Cannot cast value {value!r} as {data_type}"
        ) from exc

    raise ConfigurationError(f"Unsupported data type: {data_type}")
