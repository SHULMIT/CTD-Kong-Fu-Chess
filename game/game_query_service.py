"""
Provides read/query operations over board state.
"""

from model.board import Board
from model.position import Position


class GameQueryService:
    """
    Owns non-mutating game queries for controller and runner usage.
    """

    def __init__(
        self,
        board: Board,
    ):
        self._board = board

    @property
    def board(self) -> Board:
        """
        Returns board reference for view/formatting.
        """

        return self._board

    def is_inside(
        self,
        position: Position,
    ) -> bool:
        """
        Returns whether a position is inside board bounds.
        """

        return self._board.is_inside(position)

    def get_piece(
        self,
        position: Position,
    ):
        """
        Returns the board cell content at position.
        """

        return self._board.get_piece(position)

    def has_piece(
        self,
        position: Position,
    ) -> bool:
        """
        Returns whether a non-empty piece exists at position.
        """

        piece = self._board.get_piece(position)
        return piece is not None and piece != self._board.EMPTY_CELL