# model/board.py

from config.constants import EMPTY_SQUARE
from model.position import Position

class Board:
    """Represent the server-side board concept.

    מייצגת את רכיב השרת ``Board`` ומרכזת את התנהגותו.

    Responsibility: Represent the server-side board concept.

    אחריות: מייצגת את רכיב השרת ``Board`` ומרכזת את התנהגותו."""
    EMPTY_CELL = EMPTY_SQUARE

    def __init__(
        self,
        rows: list[list[object | None]],
    ):
        """Initialize the instance and its dependencies.

        מאתחלת את המופע ואת התלויות שלו."""
        self._rows = rows

    @property
    def width(self) -> int:
        """Perform the width operation.

        מבצעת את פעולת ``width``."""
        return len(self._rows[0]) if self._rows else 0

    @property
    def height(self) -> int:
        """Perform the height operation.

        מבצעת את פעולת ``height``."""
        return len(self._rows)

    def is_inside(self, position: Position) -> bool:
        """Check whether inside.

        בודקת אם ``inside``."""
        return (
            0 <= position.row < self.height
            and
            0 <= position.column < self.width
        )

    def get_piece(self, position: Position) -> object | None:
        """Return piece.

        מחזירה את הכלי."""
        if not self.is_inside(position):
            raise IndexError("Position outside board.")
        return self._rows[position.row][position.column]

    def set_piece(
        self,
        position: Position,
        piece: object | None,
    ) -> None:
        """Set piece.

        מגדירה את הכלי."""
        if not self.is_inside(position):
            raise IndexError("Position outside board.")
        self._rows[position.row][position.column] = piece


    def move_piece(self, source: Position, target: Position) -> None:
        """Moves a piece from source to target.

                Assumes the move has already been validated.

        מזיזה את הכלי."""
        piece = self.get_piece(source)

        if piece == self.EMPTY_CELL:
            raise ValueError("Source cell is empty.")

        self.set_piece(target, piece)
        self.set_piece(source, self.EMPTY_CELL)

        piece.position = target

