"""
Movement rule for the bishop.
"""

from model.board import Board
from model.piece import Piece
from model.position import Position

from rules.movement_rule import MovementRule
from rules.movement_utils import (
    DIAGONAL_DIRECTIONS,
    collect_moves_in_direction,
)


class BishopRule(MovementRule):
    """
    Calculates all legal bishop moves.
    """

    def get_legal_moves(
        self,
        piece: Piece,
        board: Board,
    ) -> set[Position]:

        legal_moves = set()

        for row_step, column_step in DIAGONAL_DIRECTIONS:

            legal_moves.update(
                collect_moves_in_direction(
                    board=board,
                    piece=piece,
                    row_step=row_step,
                    column_step=column_step,
                )
            )

        return legal_moves
