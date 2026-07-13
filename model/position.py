from dataclasses import dataclass


@dataclass(frozen=True)
class Position:
    """
    Represents a logical position on the board.

    This class is a value object that stores only
    the row and column of a board cell.
    """

    row: int
    column: int

    def offset(self, row_offset: int, column_offset: int):
        """
        Returns a new Position translated by the given offsets.
        """

        return Position(
            self.row + row_offset,
            self.column + column_offset,
        )

    def __str__(self):
        return f"({self.row}, {self.column})"
