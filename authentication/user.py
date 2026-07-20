"""Immutable authenticated user data."""

from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    """Represents one persisted multiplayer account."""

    id: int
    username: str
    rating: int
