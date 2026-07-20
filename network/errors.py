"""Errors exposed by the transport-independent network boundary."""


class CommandParseError(ValueError):
    """Raised when an external message is not a valid command structure."""
