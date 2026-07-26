"""Errors exposed by the transport-independent network boundary."""


class CommandParseError(ValueError):
    """Raised when an external message is not a valid command structure.

    נזרקת כאשר הודעה חיצונית אינה עומדת במבנה התקין של פקודה.

    Responsibility: Raised when an external message is not a valid command structure.

    אחריות: נזרקת כאשר הודעה חיצונית אינה עומדת במבנה התקין של פקודה."""
