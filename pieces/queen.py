# pieces/queen.py
"""
Queen — combines Rook and Bishop movement.
Can move any number of squares in a straight line or diagonally.
Cannot jump over pieces. Cannot capture a friendly piece.
"""

from pieces.piece import Piece, _is_friendly_capture, _path_is_clear
from core.position import Position


class Queen(Piece):

    def can_move(self, from_pos, to_pos, board):
        if not self._is_straight_or_diagonal(from_pos, to_pos):
            return False

        if _is_friendly_capture(from_pos, to_pos, board):
            return False

        if not _path_is_clear(from_pos, to_pos, board):
            return False

        return True

    def _is_straight_or_diagonal(self, from_pos, to_pos):
        row_diff = abs(to_pos.row - from_pos.row)
        col_diff = abs(to_pos.column - from_pos.column)

        return row_diff == 0 or col_diff == 0 or row_diff == col_diff
