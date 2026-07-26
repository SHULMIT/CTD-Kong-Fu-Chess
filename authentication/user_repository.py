"""Persistence contract used by the authentication service."""

from dataclasses import dataclass
from typing import Protocol

from authentication.user import User


@dataclass(frozen=True)
class StoredUser:
    """Server-only account record containing a password hash.

    מייצגת את רכיב השרת ``StoredUser`` ומרכזת את התנהגותו.

    Responsibility: Server-only account record containing a password hash.

    אחריות: מייצגת את רכיב השרת ``StoredUser`` ומרכזת את התנהגותו."""

    user: User
    password_hash: str


class UserRepository(Protocol):
    """Minimal account persistence required by authentication.

    מייצגת את רכיב השרת ``UserRepository`` ומרכזת את התנהגותו.

    Responsibility: Minimal account persistence required by authentication.

    אחריות: מייצגת את רכיב השרת ``UserRepository`` ומרכזת את התנהגותו."""

    def initialize(self) -> None:
        """Perform the initialize operation.

        מבצעת את פעולת ``initialize``."""
        ...

    def create(self, username: str, password_hash: str, rating: int) -> User:
        """Perform the create operation.

        מבצעת את פעולת ``create``."""
        ...

    def find_by_username(self, username: str) -> StoredUser | None:
        """Find and return by username.

        מאתרת ומחזירה את ``by`` שם המשתמש."""
        ...

    def apply_rating_update(
        self,
        game_id: str,
        winner_id: int,
        loser_id: int,
        winner_rating: int,
        loser_rating: int,
    ) -> bool: """Apply rating update.

        מחילה את הדירוג ``update``."""
        ...
