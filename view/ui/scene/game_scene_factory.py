"""Builds a fully configured game scene."""

from controller.controller import Controller
from game.game_engine import GameEngine
from view.ui.animation.animation_repository import AnimationRepository
from view.ui.constants.image_keys import ImageKeys
from view.ui.constants.ui_paths import BACKGROUND_PATH, BOARD_PATH
from view.ui.feedback.status_message_controller import StatusMessageController
from view.ui.feedback.match_started_dialog_controller import (
    MatchStartedDialogController,
)
from view.ui.graphics.image_manager import ImageManager
from view.ui.input.coordinate_scaler import CoordinateScaler
from view.ui.input.ui_input_handler import UiInputHandler
from view.ui.layout.board_layout import BoardLayout
from view.ui.render.board_renderer import BoardRenderer
from view.ui.render.overlay_renderer import OverlayRenderer
from view.ui.render.piece_layer_renderer import PieceLayerRenderer
from view.ui.render.piece_renderer import PieceRenderer
from view.ui.render.player_activity_renderer import PlayerActivityRenderer
from view.ui.scene.game_scene import GameScene
from view.ui.window.game_canvas import GameCanvas


class GameSceneFactory:
    """Creates the UI dependencies required by a game scene."""

    @staticmethod
    def create(controller: Controller, game_engine: GameEngine) -> GameScene:
        images = ImageManager()
        images.load(ImageKeys.BACKGROUND, BACKGROUND_PATH)
        canvas = GameCanvas(images.get(ImageKeys.BACKGROUND))
        layout = BoardLayout(
            window_width=canvas.width,
            window_height=canvas.height,
        )

        images.load(
            ImageKeys.BOARD,
            BOARD_PATH,
            size=(layout.board_size, layout.board_size),
        )

        board_renderer = BoardRenderer(
            canvas=canvas,
            layout=layout,
            board=images.get(ImageKeys.BOARD),
        )
        overlay_renderer = OverlayRenderer(canvas=canvas, layout=layout)
        piece_renderer = PieceRenderer(
            canvas=canvas,
            layout=layout,
            repository=AnimationRepository(),
        )
        piece_layer_renderer = PieceLayerRenderer(piece_renderer)
        player_activity_renderer = PlayerActivityRenderer(
            canvas=canvas,
            layout=layout,
            player_activity=game_engine.player_activity,
        )
        status_message_controller = StatusMessageController(overlay_renderer)
        match_started_dialog_controller = MatchStartedDialogController(
            overlay_renderer
        )
        input_handler = UiInputHandler(
            layout=layout,
            controller=controller,
            scaler=CoordinateScaler(canvas),
            report_user_error=status_message_controller.show,
        )

        return GameScene(
            controller=controller,
            game_engine=game_engine,
            canvas=canvas,
            layout=layout,
            input_handler=input_handler,
            board_renderer=board_renderer,
            piece_layer_renderer=piece_layer_renderer,
            player_activity_renderer=player_activity_renderer,
            overlay_renderer=overlay_renderer,
            status_message_controller=status_message_controller,
            match_started_dialog_controller=match_started_dialog_controller,
        )
