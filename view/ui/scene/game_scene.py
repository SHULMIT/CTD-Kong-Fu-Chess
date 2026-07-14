from view.ui.window.game_canvas import GameCanvas
from view.ui.render.board_renderer import BoardRenderer
from view.ui.layout.board_layout import BoardLayout
from view.ui.constants.ui_paths import BACKGROUND_PATH, BOARD_PATH
from view.ui.constants.image_keys import ImageKeys
from view.ui.graphics.image_manager import ImageManager
from view.ui.animation.animation_repository import AnimationRepository
from view.ui.render.piece_renderer import PieceRenderer
from model.board import Board
from model.position import Position

class GameScene:
    """
    Represents the game screen.

    Responsible for drawing all UI components
    in the correct order.
    """

    def __init__(self):
        self._image_manager = ImageManager()
        self._image_manager.load(ImageKeys.BACKGROUND, BACKGROUND_PATH)

        self._canvas = GameCanvas(
            self._image_manager.get(ImageKeys.BACKGROUND)
        )
        height, width = self._canvas.canvas.img.shape[:2]
        layout = BoardLayout(window_width=width, window_height=height)
        self._image_manager.load(
            ImageKeys.BOARD,
            BOARD_PATH,
            size=(layout.board_size, layout.board_size),
        )
        self._piece_renderer = PieceRenderer(
            canvas=self._canvas,
            layout=layout,
            repository=AnimationRepository(),
        )

        self._board = BoardRenderer(
            canvas=self._canvas,
            board_source=self._image_manager.get(ImageKeys.BOARD),
            x=layout.board_x,
            y=layout.board_y
        )

    def draw(self, board: Board | None = None) -> None:
        """
        Draws the entire game screen.
        """

        self._board.draw()

        if board is None:
            return

        for row in range(board.height):
            for column in range(board.width):
                piece = board.get_piece(Position(row, column))
                if piece is not None:
                    self._piece_renderer.draw(piece)

    def show(self) -> None:
        """
        Displays the screen.
        """

        self._canvas.show()
