class ConfigurationError(ValueError):
    """Raised when a rule configuration is invalid."""


class CircularDependencyError(ConfigurationError):
    """Raised when filter dependencies contain a cycle."""


class UnknownFilterError(ConfigurationError):
    """Raised when a condition or decision references an unknown filter."""


class UnsupportedOperatorError(ConfigurationError):
    """Raised when a configured comparison operator is not supported."""
