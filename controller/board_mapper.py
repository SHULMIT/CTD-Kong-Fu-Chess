"""
Maps screen coordinates to board positions.
"""

from config.constants import CELL_SIZE
from model.position import Position


class BoardMapper:
    """
    Converts screen coordinates to board positions.
    """

    def to_position(
        self,
        x: int,
        y: int,
    ) -> Position:
        """
        Converts pixel coordinates to a board position.
        """

        row = y // CELL_SIZE
        column = x // CELL_SIZE

        return Position(
            row=row,
            column=column,
        )