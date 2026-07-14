from view.ui.graphics.img import Img
from view.ui.window.game_canvas import GameCanvas


class BoardRenderer:
    """
    Responsible for drawing the chess board on the game canvas.
    """

    def __init__(
            self,
            canvas: GameCanvas,
            board_source: str | Img,
            x: int,
            y: int
    ):

        self._canvas = canvas
        if isinstance(board_source, Img):
            self._board = board_source
        else:
            self._board = Img().read(board_source)

        self._x = x
        self._y = y

    def draw(self) -> None:
        """
        Draws the chess board on the canvas.
        """

        self._board.draw_on(
            self._canvas.canvas,
            self._x,
            self._y
        )