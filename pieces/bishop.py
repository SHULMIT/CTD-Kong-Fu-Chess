# pieces/bishop.py
"""
Bishop — moves any number of squares diagonally.
Cannot jump over pieces. Cannot capture a friendly piece.
"""

from pieces.piece import Piece, _path_is_clear, _is_friendly_capture


class Bishop(Piece):

    def can_move(self, from_pos, to_pos, board):
        row_diff = abs(to_pos.row - from_pos.row)
        col_diff = abs(to_pos.column - from_pos.column)

        # Must move diagonally — equal non-zero steps on both axes
        if row_diff != col_diff or row_diff == 0:
            return False

        # Cannot land on a friendly piece
        if _is_friendly_capture(from_pos, to_pos, board):
            return False

        # Cannot pass through any piece
        if not _path_is_clear(from_pos, to_pos, board):
            return False

        return True
