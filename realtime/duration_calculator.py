"""
Calculates piece movement duration in milliseconds.
"""

from config.constants import MILLISECONDS_PER_CELL
from model.piece import Piece, PieceType
from model.position import Position


class DurationCalculator:
    """
    Calculates movement duration for already-validated moves.
    """

    def calculate(
        self,
        piece: Piece,
        source: Position,
        target: Position,
    ) -> int:
        """
        Returns movement duration in milliseconds.
        """

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
