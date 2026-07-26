"""Immutable authenticated user data."""

from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    """Represents one persisted multiplayer account.

    מייצגת את רכיב השרת ``User`` ומרכזת את התנהגותו.

    Responsibility: Represents one persisted multiplayer account.

    אחריות: מייצגת את רכיב השרת ``User`` ומרכזת את התנהגותו."""

    id: int
    username: str
    rating: int
