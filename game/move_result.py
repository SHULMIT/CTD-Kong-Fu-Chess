"""
Represents the outcome of a move request.

Responsibilities:
    - Store whether the move was accepted or rejected.
    - Store the reason for the result.
    - Provide convenient factory methods for creating move results.

This class is used to communicate the outcome of a move request
between the GameEngine and the Controller.
"""

from dataclasses import dataclass
from game.move_reason import MoveReason


@dataclass(frozen=True)
class MoveResult:
    """Represents the result of requesting a move.

    מייצגת את רכיב השרת ``MoveResult`` ומרכזת את התנהגותו.

    Responsibility: Represents the result of requesting a move.

    אחריות: מייצגת את רכיב השרת ``MoveResult`` ומרכזת את התנהגותו."""

    is_accepted: bool
    reason: MoveReason

    @classmethod
    def accepted(cls) -> "MoveResult":
        """Creates a successful move result.

        מבצעת את פעולת ``accepted``."""
        return cls(
            is_accepted=True,
            reason=MoveReason.OK,
        )

    @classmethod
    def rejected(cls, reason: MoveReason) -> "MoveResult":
        """Creates a rejected move result.

        מבצעת את פעולת ``rejected``."""
        return cls(
            is_accepted=False,
            reason=reason,
        )
