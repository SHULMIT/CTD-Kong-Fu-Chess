"""Persistence contract used by the authentication service."""

from dataclasses import dataclass
from typing import Protocol

from authentication.user import User


@dataclass(frozen=True)
class StoredUser:
    """Server-only account record containing a password hash."""

    user: User
    password_hash: str


class UserRepository(Protocol):
    """Minimal account persistence required by authentication."""

    def initialize(self) -> None: ...

    def create(self, username: str, password_hash: str, rating: int) -> User: ...

    def find_by_username(self, username: str) -> StoredUser | None: ...

    def apply_rating_update(
        self,
        game_id: str,
        winner_id: int,
        loser_id: int,
        winner_rating: int,
        loser_rating: int,
    ) -> bool: ...
