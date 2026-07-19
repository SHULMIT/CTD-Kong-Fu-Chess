from config.constants import BOARD_SIZE
from model.position import Position


class BoardLayout:
    """
    board_layout.py

    Contains the BoardLayout class.

    The BoardLayout class belongs to the UI layer and is responsible
    for calculating the graphical layout of the chess board.

    Responsibilities:
        - Calculate the board size.
        - Calculate the size of each square.
        - Center the board inside the window.
        - Convert board coordinates to screen coordinates.
        - Convert screen coordinates to board coordinates.

    The class does NOT draw anything.
    It only performs layout calculations.
    """

    def __init__(
            self,
            window_width: int,
            window_height: int,
            board_ratio: float = 0.8,
            board_inner_ratio: float = 0.8,
    ):
       

        self.window_width = window_width
        self.window_height = window_height

        self.board_ratio = board_ratio
        self.board_inner_ratio = board_inner_ratio

        # Board size
        self.board_size = int(
            min(window_width, window_height) * board_ratio
        )

        # Center the board
        self.board_x = (window_width - self.board_size) // 2
        self.board_y = (window_height - self.board_size) // 2

        # Board.jpg has a decorative wooden frame. The playable board area is
        # the centered 80% of that image, so pieces must use this inner area.
        self.inner_board_size = int(self.board_size * board_inner_ratio)
        self.square_size = self.inner_board_size // BOARD_SIZE
        self.cells_x = self.board_x + (self.board_size - self.inner_board_size) // 2
        self.cells_y = self.board_y + (self.board_size - self.inner_board_size) // 2

    def cell_to_pixel(self, position: Position) -> tuple[int, int]:
      

        x = self.cells_x + position.column * self.square_size
        y = self.cells_y + position.row * self.square_size

        return x, y

    def pixel_to_cell(self, x: int, y: int) -> Position:


        column = (x - self.cells_x) // self.square_size
        row = (y - self.cells_y) // self.square_size

        return Position(row, column)

    def is_inside_board(self, x: int, y: int) -> bool:
        """
        Checks whether a pixel is inside the board.
        """

        return (
                self.cells_x <= x < self.cells_x + self.inner_board_size
                and
                self.cells_y <= y < self.cells_y + self.inner_board_size
        )
