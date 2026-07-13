# model/board.py

from config.constants import EMPTY_SQUARE
from model.position import Position

class Board:
    EMPTY_CELL = EMPTY_SQUARE

    def __init__(
        self,
        rows: list[list[object | None]],
    ):
        self._rows = rows

    @property
    def width(self) -> int:
        return len(self._rows[0]) if self._rows else 0

    @property
    def height(self) -> int:
        return len(self._rows)

    def is_inside(self, position: Position) -> bool:
        return (
            0 <= position.row < self.height
            and
            0 <= position.column < self.width
        )

    def get_piece(self, position: Position) -> object | None:
        if not self.is_inside(position):
            raise IndexError("Position outside board.")
        return self._rows[position.row][position.column]

    def set_piece(
        self,
        position: Position,
        piece: object | None,
    ) -> None:
        if not self.is_inside(position):
            raise IndexError("Position outside board.")
        self._rows[position.row][position.column] = piece


    def move_piece(self, source: Position, target: Position) -> None:
        """
        Moves a piece from source to target.

        Assumes the move has already been validated.
        """
        piece = self.get_piece(source)

        if piece == self.EMPTY_CELL:
            raise ValueError("Source cell is empty.")

        self.set_piece(target, piece)
        self.set_piece(source, self.EMPTY_CELL)

        piece.position = target

