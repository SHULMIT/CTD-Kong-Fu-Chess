# pieces/rook.py
"""
Rook — moves any number of squares in a straight line (horizontal or vertical).
Cannot jump over pieces. Cannot capture a friendly piece.
"""

from pieces.piece import Piece, _path_is_clear, _is_friendly_capture


class Rook(Piece):

    def can_move(self, from_pos, to_pos, board):
        moved_row = from_pos.row != to_pos.row
        moved_col = from_pos.column != to_pos.column

        # Must move along exactly one axis (XOR)
        if moved_row == moved_col:
            return False

        # Cannot land on a friendly piece
        if _is_friendly_capture(from_pos, to_pos, board):
            return False

        # Cannot pass through any piece
        if not _path_is_clear(from_pos, to_pos, board):
            return False

        return True
