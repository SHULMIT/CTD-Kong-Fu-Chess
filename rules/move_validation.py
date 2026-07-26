"""
Represents the result of move validation.
"""

from dataclasses import dataclass

from game.move_reason import MoveReason


@dataclass(frozen=True)
class MoveValidation:
    """Represents the result of validating a move.

    מייצגת את רכיב השרת ``MoveValidation`` ומרכזת את התנהגותו.

    Responsibility: Represents the result of validating a move.

    אחריות: מייצגת את רכיב השרת ``MoveValidation`` ומרכזת את התנהגותו."""

    is_valid: bool
    reason: MoveReason
