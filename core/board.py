from core.position import Position


class Board:
    """
    Represents the game board.
    Responsible only for storing the board state.
    """

    EMPTY_CELL = "."

    def __init__(self, rows: list[list[str]]):
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

    def get_piece(self, position: Position) -> str:
        if not self.is_inside(position):
            raise IndexError("Position outside board.")

        return self._rows[position.row][position.column]

    def set_piece(self, position: Position, piece: str) -> None:
        if not self.is_inside(position):
            raise IndexError("Position outside board.")

        self._rows[position.row][position.column] = piece

    def get_rows(self) -> list[list[str]]:
        return self._rows