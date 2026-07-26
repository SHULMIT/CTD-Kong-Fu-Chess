"""
Manages all active motions.
"""

from typing import List

from model.piece import Piece
from realtime.motion import Motion


class MotionManager:
    """Stores and manages all active motions.

    מייצגת את רכיב השרת ``MotionManager`` ומרכזת את התנהגותו.

    Responsibility: Stores and manages all active motions.

    אחריות: מייצגת את רכיב השרת ``MotionManager`` ומרכזת את התנהגותו."""

    def __init__(self):
        """Initialize the instance and its dependencies.

        מאתחלת את המופע ואת התלויות שלו."""
        self._motions: List[Motion] = []

    def add(
        self,
        motion: Motion,
    ) -> None:
        """Perform the add operation.

        מבצעת את פעולת ``add``."""
        self._motions.append(motion)

    def remove(
        self,
        motion: Motion,
    ) -> None:
        """Perform the remove operation.

        מבצעת את פעולת ``remove``."""
        self._motions.remove(motion)

    def get_all(self) -> List[Motion]:
        """Return all.

        מחזירה את ``all``."""
        return self._motions

    def get_snapshot(self) -> tuple[Motion, ...]:
        """Returns an immutable snapshot of active motions — safe for external use.

        מחזירה את תמונת המצב."""
        return tuple(self._motions)

    def is_piece_moving(
        self,
        piece: Piece,
    ) -> bool:
        """Check whether piece moving.

        בודקת אם הכלי ``moving``."""
        return any(
            motion.piece == piece
            for motion in self._motions
        )

    def has_motions(self) -> bool:
        """Check whether there is motions.

        בודקת אם קיים ``motions``."""
        return len(self._motions) > 0
