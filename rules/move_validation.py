"""
Represents the result of move validation.
"""

from dataclasses import dataclass

from game.move_reason import MoveReason


@dataclass(frozen=True)
class MoveValidation:
    """
    Represents the result of validating a move.
    """

    is_valid: bool
    reason: MoveReason
