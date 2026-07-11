# core/board.py

from config.constants import EMPTY_SQUARE

class Board:
    EMPTY_CELL = EMPTY_SQUARE

    def __init__(self, rows):
        self._rows = rows

    @property
    def width(self):
        return len(self._rows[0]) if self._rows else 0

    @property
    def height(self):
        return len(self._rows)

    def is_inside(self, position):
        return (
            0 <= position.row < self.height
            and
            0 <= position.column < self.width
        )

    def get_piece(self, position):
        if not self.is_inside(position):
            raise IndexError("Position outside board.")
        return self._rows[position.row][position.column]

    def set_piece(self, position, piece):
        if not self.is_inside(position):
            raise IndexError("Position outside board.")
        self._rows[position.row][position.column] = piece