"""Composition root for the local desktop game application."""

from app.game_application import GameApplication
from app.game_engine_factory import GameEngineFactory
from controller.controller import Controller
from view.ui.scene.game_scene_factory import GameSceneFactory


class DesktopApplicationFactory:
    """Builds the desktop UI around an independently created game engine."""

    @staticmethod
    def create() -> GameApplication:
        """Return a fully configured local desktop application."""

        game_engine = GameEngineFactory.create()
        controller = Controller(game_engine=game_engine)
        scene = GameSceneFactory.create(
            controller=controller,
            game_engine=game_engine,
        )
        return GameApplication(scene=scene)
