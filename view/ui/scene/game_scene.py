import time

from model.position import Position
from model.piece import Piece, PieceColor, PieceType

from view.ui.constants.image_keys import ImageKeys
from view.ui.constants.ui_paths import BACKGROUND_PATH, BOARD_PATH

from view.ui.graphics.image_manager import ImageManager
from view.ui.input.coordinate_scaler import CoordinateScaler
from view.ui.input.ui_input_handler import UiInputHandler
from view.ui.layout.board_layout import BoardLayout
from view.ui.animation.animation_repository import AnimationRepository
from view.ui.render.board_renderer import BoardRenderer
from view.ui.render.overlay_renderer import OverlayRenderer
from view.ui.render.piece_renderer import PieceRenderer
from view.ui.render.player_activity_renderer import PlayerActivityRenderer
from view.ui.window.game_canvas import GameCanvas
from controller.controller import Controller
from game.game_engine import GameEngine

class GameScene:
    """

    STATUS_MESSAGE_DURATION_SECONDS = 2.0
    game_scene.py

    Builds and renders the game scene.

    Responsibilities:
        - Create the UI components.
        - Coordinate all renderers.
        - Draw the current frame.
    """

    def __init__(
    self,
    controller: Controller,
    game_engine: GameEngine,):
        self._controller = controller
        self._game_engine = game_engine
        self._images = ImageManager()

        self._images.load(
            ImageKeys.BACKGROUND,
            BACKGROUND_PATH,
        )

        background = self._images.get(
            ImageKeys.BACKGROUND
        )

        self._canvas = GameCanvas(background)

        self._layout = BoardLayout(
            window_width=self._canvas.width,
            window_height=self._canvas.height,
        )

        self._images.load(
            ImageKeys.BOARD,
            BOARD_PATH,
            size=(
                self._layout.board_size,
                self._layout.board_size,
            ),
        )

        self._board_renderer = BoardRenderer(
            canvas=self._canvas,
            layout=self._layout,
            board=self._images.get(
                ImageKeys.BOARD
            ),
        )

        self._overlay_renderer = OverlayRenderer(
            canvas=self._canvas,
            layout=self._layout,
        )
        self._piece_renderer = PieceRenderer(
            canvas=self._canvas,
            layout=self._layout,
            repository=AnimationRepository(),
        )
        self._player_activity_renderer = PlayerActivityRenderer(
            canvas=self._canvas,
            layout=self._layout,
            player_activity=self._game_engine.player_activity,
        )
        self._input_handler = UiInputHandler(
            layout=self._layout,
            controller=self._controller,
            scaler=CoordinateScaler(self._canvas),
            report_user_error=self._show_user_error,
        )
        self._status_message: str | None = None
        self._status_message_expires_at = 0.0
    @property
    def canvas(self) -> GameCanvas:
        return self._canvas

    @property
    def layout(self) -> BoardLayout:
        return self._layout

    @property
    def is_game_over(self) -> bool:
        """Returns whether the game has ended."""
        return self._game_engine.game_over

    def bind_input(self) -> None:
        """Registers this scene's mouse handler after the window exists."""
        self._canvas.set_mouse_callback(
            self._input_handler.handle_mouse,
        )

    def update(self, delta_time: float) -> None:
        """Advances the game simulation by the elapsed frame time in seconds."""
        milliseconds = round(delta_time * 1000)
        if milliseconds > 0:
            self._game_engine.wait(milliseconds)

    def draw(
        self,
        selected_position: Position | None = None,
    ) -> None:
        """
        Draws the current game frame.
        """

        # Erase the previous frame by resetting to the original background.
        self._canvas.reset()

        self._board_renderer.draw()

        board = self._game_engine.board
        active_motions = self._game_engine.get_motions()
        for row in range(board.height):
            for column in range(board.width):
                piece = board.get_piece(Position(row, column))
                if isinstance(piece, Piece):
                    self._piece_renderer.draw(piece, active_motions)

        self._player_activity_renderer.draw()

        self._draw_status_message()

        if self._game_engine.game_over:
            self._overlay_renderer.draw_game_over(
                self._resolve_winner()
            )
        else:
            selected = selected_position or self._controller.selected_position
            self._overlay_renderer.draw_selected(selected)
            if selected is not None:
                legal = self._game_engine.get_legal_moves(selected)
                self._overlay_renderer.draw_legal_moves(legal)

    def _resolve_winner(self) -> str:
        """
        Returns a winner string by checking which king is still on the board.
        """
        board = self._game_engine.board
        white_king_alive = False
        black_king_alive = False

        for row in range(board.height):
            for column in range(board.width):
                piece = board.get_piece(Position(row, column))
                if isinstance(piece, Piece) and piece.type == PieceType.KING:
                    if piece.color == PieceColor.WHITE:
                        white_king_alive = True
                    else:
                        black_king_alive = True

        if white_king_alive and not black_king_alive:
            return "White wins!"
        if black_king_alive and not white_king_alive:
            return "Black wins!"
        return "Game Over"

    def _show_user_error(self, message: str) -> None:
        """Shows an expected input error without interrupting the game loop."""
        self._status_message = message
        self._status_message_expires_at = (
            time.perf_counter() + self.STATUS_MESSAGE_DURATION_SECONDS
        )

    def _draw_status_message(self) -> None:
        if self._status_message is None:
            return
        if time.perf_counter() >= self._status_message_expires_at:
            self._status_message = None
            return
        self._overlay_renderer.draw_status_message(self._status_message)

    def show(self) -> None:
        """
        Displays the current frame.
        """

        self._canvas.present()
