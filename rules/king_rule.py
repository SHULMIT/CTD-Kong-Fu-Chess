"""
Movement rule for the king.
"""

from model.board import Board
from model.piece import Piece
from model.position import Position

from rules.movement_rule import MovementRule
from rules.movement_utils import (
    DIAGONAL_DIRECTIONS,
    ORTHOGONAL_DIRECTIONS,
    is_empty_square,
    is_enemy_piece,
)


class KingRule(MovementRule):
    """
    Calculates all legal king moves.
    """

    def get_legal_moves(
        self,
        piece: Piece,
        board: Board,
    ) -> set[Position]:

        legal_moves = set()

        for row_offset, column_offset in (
            ORTHOGONAL_DIRECTIONS + DIAGONAL_DIRECTIONS
        ):

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
