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
    """
    Represents the result of requesting a move.
    """

    is_accepted: bool
    reason: MoveReason

    @classmethod
    def accepted(cls) -> "MoveResult":
        """
        Creates a successful move result.
        """
        return cls(
            is_accepted=True,
            reason=MoveReason.OK,
        )

    @classmethod
    def rejected(cls, reason: MoveReason) -> "MoveResult":
        """
        Creates a rejected move result.
        """
        return cls(
            is_accepted=False,
            reason=reason,
        )
