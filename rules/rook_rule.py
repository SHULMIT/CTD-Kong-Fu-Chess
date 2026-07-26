"""
Movement rule for the rook.
"""

from model.board import Board
from model.piece import Piece
from model.position import Position

from rules.movement_rule import MovementRule
from rules.movement_utils import (
    ORTHOGONAL_DIRECTIONS,
    collect_moves_in_direction,
)


class RookRule(MovementRule):
    """Calculates all legal rook moves.

    מייצגת את רכיב השרת ``RookRule`` ומרכזת את התנהגותו.

    Responsibility: Calculates all legal rook moves.

    אחריות: מייצגת את רכיב השרת ``RookRule`` ומרכזת את התנהגותו."""

    def get_legal_moves(
        self,
        piece: Piece,
        board: Board,
    ) -> set[Position]:

        """Return legal moves.

        מחזירה את ``legal`` המהלכים."""
        legal_moves = set()

        for row_step, column_step in ORTHOGONAL_DIRECTIONS:

            legal_moves.update(
                collect_moves_in_direction(
                    board=board,
                    piece=piece,
                    row_step=row_step,
                    column_step=column_step,
                )
            )

        return legal_moves
