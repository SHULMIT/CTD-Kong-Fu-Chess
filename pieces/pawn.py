# pieces/pawn.py
"""
Pawn movement rules:
  - Moves one square forward (direction depends on color):
      White ('w'): moves upward   → row decreases by 1
      Black ('b'): moves downward → row increases by 1
  - Can capture diagonally forward (one step forward + one step sideways),
    but only if an enemy piece occupies that square.
  - Cannot capture forward (straight ahead is blocked by any piece).
  - Cannot move two squares (double step is not supported in this iteration).
  - Cannot capture a friendly piece.
"""

from pieces.piece import Piece, _is_friendly_capture


class Pawn(Piece):

    def __init__(self, color):
        # 'w' = white (moves up, row decreases), 'b' = black (moves down, row increases)
        self._color = color
        self._forward = -1 if color == 'w' else 1

    def can_move(self, from_pos, to_pos, board):
        row_diff = to_pos.row - from_pos.row
        col_diff = abs(to_pos.column - from_pos.column)

        # Must move exactly one step forward
        if row_diff != self._forward:
            return False

        if col_diff == 0:
            # Straight forward — only allowed if the target square is empty
            return self._can_move_forward(to_pos, board)

        if col_diff == 1:
            # Diagonal — only allowed as a capture of an enemy piece
            return self._can_capture_diagonal(from_pos, to_pos, board)

        # Any other column difference is illegal
        return False

    def _can_move_forward(self, to_pos, board):
        """Straight forward move: target must be empty."""
        return board.get_piece(to_pos) == board.EMPTY_CELL

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
