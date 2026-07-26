"""Base data type for events exchanged between application components."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Event:
    """Base type for all application and game events.

    מייצגת את רכיב השרת ``Event`` ומרכזת את התנהגותו.

    Responsibility: Base type for all application and game events.

    אחריות: מייצגת את רכיב השרת ``Event`` ומרכזת את התנהגותו."""
