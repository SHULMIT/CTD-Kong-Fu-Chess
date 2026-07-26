"""
Calculates piece movement duration in milliseconds.
"""

from config.constants import MILLISECONDS_PER_CELL
from model.piece import Piece, PieceType
from model.position import Position


class DurationCalculator:
    """Calculates movement duration for already-validated moves.

    מייצגת את רכיב השרת ``DurationCalculator`` ומרכזת את התנהגותו.

    Responsibility: Calculates movement duration for already-validated moves.

    אחריות: מייצגת את רכיב השרת ``DurationCalculator`` ומרכזת את התנהגותו."""

    def calculate(
        self,
        piece: Piece,
        source: Position,
        target: Position,
    ) -> int:
        """Returns movement duration in milliseconds.

        מבצעת את פעולת ``calculate``."""

        if piece.type == PieceType.KNIGHT:
            distance_in_cells = 1
        else:
            row_delta = abs(target.row - source.row)
            column_delta = abs(target.column - source.column)

            if source.row == target.row:
                distance_in_cells = column_delta
            elif source.column == target.column:
                distance_in_cells = row_delta
            else:
                distance_in_cells = row_delta

        return distance_in_cells * MILLISECONDS_PER_CELL
