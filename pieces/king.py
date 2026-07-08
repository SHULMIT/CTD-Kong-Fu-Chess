# pieces/king.py
"""
King — moves exactly one square in any direction (horizontal, vertical, diagonal).
Cannot capture a friendly piece.
"""

from pieces.piece import Piece, _is_friendly_capture


class King(Piece):

    def can_move(self, from_pos, to_pos, board):
        row_diff = abs(to_pos.row - from_pos.row)
        col_diff = abs(to_pos.column - from_pos.column)

        # Must move exactly one square on at least one axis
        if max(row_diff, col_diff) != 1:
            return False

        # Cannot land on a friendly piece
        if _is_friendly_capture(from_pos, to_pos, board):
            return False

        return True
