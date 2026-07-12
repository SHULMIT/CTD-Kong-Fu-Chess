"""
Defines the interface for all chess movement rules.
"""

from abc import ABC, abstractmethod

from model.board import Board
from model.piece import Piece
from model.position import Position


class MovementRule(ABC):
    """
    Base interface for all piece movement rules.
    """

    @abstractmethod
    def get_legal_moves(
        self,
        piece: Piece,
        board: Board,
    ) -> set[Position]:
        pass
