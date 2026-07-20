"""Composition root for creating independent game-domain engines."""

from board_io.board_loader import BoardLoader
from config.constants import DEFAULT_BOARD_PATH
from game.game_engine import GameEngine
from game.player_activity_service import PlayerActivityService
from realtime.duration_calculator import DurationCalculator
from realtime.real_time_arbiter import RealTimeArbiter
from rules.rule_engine import RuleEngine


class GameEngineFactory:
    """Creates fully initialized games without UI dependencies."""

    @staticmethod
    def create() -> GameEngine:
        """Return a new engine with independent domain and simulation state."""

        board = BoardLoader.load(DEFAULT_BOARD_PATH)
        player_activity = PlayerActivityService()
        arbiter = RealTimeArbiter(
            board,
            player_activity=player_activity,
        )

        return GameEngine(
            board=board,
            rule_engine=RuleEngine(),
            arbiter=arbiter,
            duration_calculator=DurationCalculator(),
            player_activity=player_activity,
        )
