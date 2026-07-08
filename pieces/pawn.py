# pieces/pawn.py
"""
Pawn — moves one square forward (direction depends on color).
  White ('w'): advances downward (row increases).
  Black ('b'): advances upward (row decreases).
Cannot capture a friendly piece.
Note: diagonal captures and double opening moves are not implemented in this iteration.
"""

from pieces.piece import Piece, _is_friendly_capture


class Pawn(Piece):

    def __init__(self, color):
        self._color = color

    def can_move(self, from_pos, to_pos, board):
        col_diff = abs(to_pos.column - from_pos.column)
        row_diff = to_pos.row - from_pos.row

        # Must stay in the same column
        if col_diff != 0:
            return False

        # Direction depends on color
        expected_step = 1 if self._color == 'w' else -1
        if row_diff != expected_step:
            return False

        # Cannot land on a friendly piece
        if _is_friendly_capture(from_pos, to_pos, board):
            return False

        return True
