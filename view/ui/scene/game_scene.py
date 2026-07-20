"""Coordinates updates and rendering for the game scene."""

from controller.controller import Controller
from game.game_engine import GameEngine
from model.position import Position
from view.ui.feedback.status_message_controller import StatusMessageController
from view.ui.feedback.match_started_dialog_controller import (
    MatchStartedDialogController,
)
from view.ui.input.ui_input_handler import UiInputHandler
from view.ui.layout.board_layout import BoardLayout
from view.ui.render.board_renderer import BoardRenderer
from view.ui.render.overlay_renderer import OverlayRenderer
from view.ui.render.piece_layer_renderer import PieceLayerRenderer
from view.ui.render.player_activity_renderer import PlayerActivityRenderer
from view.ui.window.game_canvas import GameCanvas


class GameScene:
    """Coordinates input, simulation updates, and rendering for the game scene."""
    def __init__(
        self,
        controller: Controller,
        game_engine: GameEngine,
        canvas: GameCanvas,
        layout: BoardLayout,
        input_handler: UiInputHandler,
        board_renderer: BoardRenderer,
        piece_layer_renderer: PieceLayerRenderer,
        player_activity_renderer: PlayerActivityRenderer,
        overlay_renderer: OverlayRenderer,
        status_message_controller: StatusMessageController,
        match_started_dialog_controller: MatchStartedDialogController | None = None,
    ) -> None:
        self._controller = controller
        self._game_engine = game_engine
        self._canvas = canvas
        self._layout = layout
        self._input_handler = input_handler
        self._board_renderer = board_renderer
        self._piece_layer_renderer = piece_layer_renderer
        self._player_activity_renderer = player_activity_renderer
        self._overlay_renderer = overlay_renderer
        self._status_message_controller = status_message_controller
        self._match_started_dialog_controller = match_started_dialog_controller

    @property
    def canvas(self) -> GameCanvas:
        return self._canvas

    @property
    def layout(self) -> BoardLayout:
        return self._layout

    @property
    def is_game_over(self) -> bool:
        """Return whether the game has ended."""
        return self._game_engine.game_over

    @property
    def should_close(self) -> bool:
        provider = getattr(type(self._game_engine), "should_close_spectator_view", None)
        return bool(provider(self._game_engine)) if provider is not None else False

    def bind_input(self) -> None:
        """Register this scene's mouse handler after the window exists."""
        self._canvas.set_mouse_callback(self._input_handler.handle_mouse)

    def update(self, delta_time: float) -> None:
        """Advance input and game simulation by the elapsed frame time."""
        self._input_handler.update()
        milliseconds = round(delta_time * 1000)
        if milliseconds > 0:
            self._game_engine.wait(milliseconds)
        consume_message = getattr(
            self._game_engine,
            "consume_match_started_message",
            None,
        )
        if consume_message is not None and self._match_started_dialog_controller:
            message = consume_message()
            if message is not None:
                self._match_started_dialog_controller.show(message)

    def draw(self, selected_position: Position | None = None) -> None:
        """Draw the current game frame in scene-layer order."""
        self._canvas.reset()
        self._board_renderer.draw()
        self._piece_layer_renderer.draw(
            self._game_engine.board,
            self._game_engine.get_motions(),
        )
        self._player_activity_renderer.draw()
        self._status_message_controller.draw()
        self._draw_overlays(selected_position)
        if self._match_started_dialog_controller is not None:
            self._match_started_dialog_controller.draw()
        disconnect_provider = getattr(
            type(self._game_engine), "disconnect_overlay_message", None
        )
        disconnect_message = (
            disconnect_provider(self._game_engine)
            if disconnect_provider is not None
            else None
        )
        if disconnect_message:
            self._overlay_renderer.draw_disconnect_status(disconnect_message)

    def _draw_overlays(self, selected_position: Position | None) -> None:
        if self._game_engine.game_over:
            winner = self._game_engine.get_winner()
            winner_message = (
                f"{winner.name.title()} wins!"
                if winner is not None
                else "Game Over"
            )
            self._overlay_renderer.draw_game_over(winner_message)
            return

        selected = selected_position or self._controller.selected_position
        self._overlay_renderer.draw_selected(selected)
        if selected is not None:
            legal_moves = self._game_engine.get_legal_moves(selected)
            self._overlay_renderer.draw_legal_moves(legal_moves)

    def show(self) -> None:
        """Display the current frame."""
        self._canvas.present()
