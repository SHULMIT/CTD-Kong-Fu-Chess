"""
Manages all active motions.
"""

from typing import List

from model.piece import Piece
from realtime.motion import Motion


class MotionManager:
    """
    Stores and manages all active motions.
    """

    def __init__(self):
        self._motions: List[Motion] = []

    def add(
        self,
        motion: Motion,
    ) -> None:
        self._motions.append(motion)

    def remove(
        self,
        motion: Motion,
    ) -> None:
        self._motions.remove(motion)

    def get_all(self) -> List[Motion]:
        return self._motions

    def is_piece_moving(
        self,
        piece: Piece,
    ) -> bool:
        return any(
            motion.piece == piece
            for motion in self._motions
        )

    def has_motions(self) -> bool:
        return len(self._motions) > 0
