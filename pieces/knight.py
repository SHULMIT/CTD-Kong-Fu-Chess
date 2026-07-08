# pieces/knight.py
"""
Knight — moves in an L-shape (2+1 or 1+2 squares).
Can jump over other pieces. Cannot capture a friendly piece.
"""

from pieces.piece import Piece, _is_friendly_capture


class Knight(Piece):

    def can_move(self, from_pos, to_pos, board):
        row_diff = abs(to_pos.row - from_pos.row)
        col_diff = abs(to_pos.column - from_pos.column)

        # L-shape: differences must be exactly 1 and 2 in some order
        if sorted([row_diff, col_diff]) != [1, 2]:
            return False

        # Cannot land on a friendly piece (but can jump over anything)
        if _is_friendly_capture(from_pos, to_pos, board):
            return False

        return True
