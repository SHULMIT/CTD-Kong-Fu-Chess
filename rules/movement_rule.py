"""
Defines the interface for all chess movement rules.
"""

from abc import ABC, abstractmethod

from model.board import Board
from model.piece import Piece
from model.position import Position


class MovementRule(ABC):
    """Base interface for all piece movement rules.

    מייצגת את רכיב השרת ``MovementRule`` ומרכזת את התנהגותו.

    Responsibility: Base interface for all piece movement rules.

    אחריות: מייצגת את רכיב השרת ``MovementRule`` ומרכזת את התנהגותו."""

    @abstractmethod
    def get_legal_moves(
        self,
        piece: Piece,
        board: Board,
    ) -> set[Position]:
        """Return legal moves.

        מחזירה את ``legal`` המהלכים."""
        pass
