"""
Represents the result of requesting a move.
"""

from dataclasses import dataclass
from enum import Enum


class MoveReason(Enum):
    """
    Possible results returned by GameEngine.
    """

    OK = "ok"

    GAME_OVER = "game_over"

    MOTION_IN_PROGRESS = "motion_in_progress"

    OUTSIDE_BOARD = "outside_board"

    EMPTY_SOURCE = "empty_source"

    FRIENDLY_DESTINATION = "friendly_destination"

    ILLEGAL_PIECE_MOVE = "illegal_piece_move"


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