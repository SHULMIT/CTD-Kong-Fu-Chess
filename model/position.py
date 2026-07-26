from dataclasses import dataclass


@dataclass(frozen=True)
class Position:
    """Represents a logical position on the board.

        This class is a value object that stores only
        the row and column of a board cell.

    מייצגת את רכיב השרת ``Position`` ומרכזת את התנהגותו.

    Responsibility: Represents a logical position on the board.

    אחריות: מייצגת את רכיב השרת ``Position`` ומרכזת את התנהגותו."""

    row: int
    column: int

    def offset(self, row_offset: int, column_offset: int):
        """Returns a new Position translated by the given offsets.

        מבצעת את פעולת ``offset``."""

        return Position(
            self.row + row_offset,
            self.column + column_offset,
        )

    def __str__(self):
        """Return a readable string representation.

        מחזירה ייצוג טקסטואלי קריא."""
        return f"({self.row}, {self.column})"
