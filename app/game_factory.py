"""
game_factory.py

Builds the game application.
"""

from board_io.board_loader import BoardLoader

from config.constants import DEFAULT_BOARD_PATH

from controller.controller import Controller

from app.game_application import GameApplication

from game.game_engine import GameEngine

from realtime.duration_calculator import DurationCalculator
from realtime.real_time_arbiter import RealTimeArbiter

from rules.rule_engine import RuleEngine

from view.ui.scene.game_scene import GameScene


class GameFactory:

    @staticmethod
    def create() -> GameApplication:

        board = BoardLoader.load(
            DEFAULT_BOARD_PATH
        )

        rule_engine = RuleEngine()

        arbiter = RealTimeArbiter(
            board
        )

        duration_calculator = DurationCalculator()

        game_engine = GameEngine(
            board=board,
            rule_engine=rule_engine,
            arbiter=arbiter,
            duration_calculator=duration_calculator,
        )

        controller = Controller(
            game_engine=game_engine,
        )

        scene = GameScene(
            controller=controller,
            game_engine=game_engine,
        )

        return GameApplication(
            scene=scene
        )
