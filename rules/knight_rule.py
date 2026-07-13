"""
Movement rule for the knight.
"""

from model.board import Board
from model.piece import Piece
from model.position import Position

from rules.movement_rule import MovementRule
from rules.movement_utils import (
    is_empty_square,
    is_enemy_piece,
)


KNIGHT_OFFSETS = (
    (-2, -1),
    (-2, 1),
    (-1, -2),
    (-1, 2),
    (1, -2),
    (1, 2),
    (2, -1),
    (2, 1),
)


class KnightRule(MovementRule):
    """
    Calculates all legal knight moves.
    """

    def get_legal_moves(
        self,
        piece: Piece,
        board: Board,
    ) -> set[Position]:

        legal_moves = set()

        for row_offset, column_offset in KNIGHT_OFFSETS:

            position = piece.position.offset(
                row_offset,
                column_offset,
            )

            if not board.is_inside(position):
                continue

            target = board.get_piece(position)

            if (
                is_empty_square(target)
                or is_enemy_piece(piece, target)
            ):
                legal_moves.add(position)

        return legal_moves
