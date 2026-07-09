# pieces/pawn.py
"""
Pawn movement rules:
  - Moves one square forward (direction depends on color):
      White ('w'): moves upward   → row decreases by 1
      Black ('b'): moves downward → row increases by 1
  - Can make a two-square move from its starting row if the path is clear.
  - Can capture diagonally forward (one step forward + one step sideways),
    but only if an enemy piece occupies that square.
  - Cannot capture forward (straight ahead is blocked by any piece).
  - Cannot capture a friendly piece.
"""

from pieces.piece import Piece, _is_friendly_capture
from core.position import Position


class Pawn(Piece):

    def __init__(self, color):
        self._color = color

    def can_move(self, from_pos, to_pos, board):
        row_diff = to_pos.row - from_pos.row
        col_diff = abs(to_pos.column - from_pos.column)

        if col_diff == 0:
            return self._can_move_forward(from_pos, to_pos, board)

        if col_diff == 1:
            return self._can_capture_diagonal(from_pos, to_pos, board)

        return False

    def _can_move_forward(self, from_pos, to_pos, board):
        """Straight forward move: target must be empty and the path must be clear."""
        if board.get_piece(to_pos) != board.EMPTY_CELL:
            return False

        forward = self._forward_dir(board)

        if to_pos.row == from_pos.row + forward:
            return True

        if self._is_start_row(from_pos, board) and to_pos.row == from_pos.row + (2 * forward):
            middle = Position(from_pos.row + forward, from_pos.column)
            return board.get_piece(middle) == board.EMPTY_CELL

        return False

    def _is_start_row(self, pos, board):
        """True for a pawn on its initial row for the current board size."""
        if self._color == 'w':
            return pos.row == self._white_start_row(board)
        return pos.row == self._black_start_row(board)

    def _forward_dir(self, board):
        if self._color == 'w':
            return -1
        return -1 if board.height >= 6 else 1

    def _white_start_row(self, board):
        return board.height - 1 if board.height <= 4 else board.height - 2

    def _black_start_row(self, board):
        return 0 if board.height <= 4 else 1

    def _can_capture_diagonal(self, from_pos, to_pos, board):
        """
        Diagonal capture: target must hold an enemy piece.
        Cannot capture a friendly piece diagonally either.
        """
        target = board.get_piece(to_pos)

        # Target must not be empty (no capturing thin air)
        if target == board.EMPTY_CELL:
            return False

        # Target must not be a friendly piece
        if _is_friendly_capture(from_pos, to_pos, board):
            return False

        return True
