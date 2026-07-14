from view.ui.graphics.img import Img
from view.ui.layout.board_layout import BoardLayout
from view.ui.window.game_canvas import GameCanvas


class BoardRenderer:
    """
    board_renderer.py

    Contains the BoardRenderer class.

    The BoardRenderer belongs to the UI layer and is responsible
    for drawing the chess board on the game canvas.

    Responsibilities:
        - Draw the board image.
        - Use the layout to determine where to draw the board.

    The renderer does NOT:
        - Load images.
        - Calculate positions.
        - Know anything about chess rules.
    """

    def __init__(
            self,
            canvas: GameCanvas,
            layout: BoardLayout,
            board: Img
    ):
        self._canvas = canvas
        self._layout = layout
        self._board = board

    def draw(self) -> None:
        """
        Draw the board on the canvas.
        """

        self._board.draw_on(
            self._canvas.canvas,
            self._layout.board_x,
            self._layout.board_y
        )