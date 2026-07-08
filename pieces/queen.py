# pieces/queen.py
"""
Queen — combines Rook and Bishop movement.
Can move any number of squares in a straight line or diagonally.
Cannot jump over pieces. Cannot capture a friendly piece.
"""

from pieces.piece import Piece
from pieces.rook import Rook
from pieces.bishop import Bishop


class Queen(Piece):

    def __init__(self):
        self._rook = Rook()
        self._bishop = Bishop()

    def can_move(self, from_pos, to_pos, board):
        return (
            self._rook.can_move(from_pos, to_pos, board)
            or
            self._bishop.can_move(from_pos, to_pos, board)
        )
