"""
Handles move-request flow from validation to motion scheduling.
"""

from game.move_result import MoveResult
from model.board import Board
from model.position import Position
from realtime.duration_calculator import DurationCalculator
from realtime.real_time_arbiter import RealTimeArbiter
from rules.rule_engine import RuleEngine


class RequestMoveService:
    """
    Owns a single responsibility: process legal move requests.

    This service does not know about game-over lifecycle decisions.
    """

    def __init__(
        self,
        board: Board,
        rule_engine: RuleEngine,
        arbiter: RealTimeArbiter,
        duration_calculator: DurationCalculator,
    ):
        self._board = board
        self._rule_engine = rule_engine
        self._arbiter = arbiter
        self._duration_calculator = duration_calculator

    def request_move(
        self,
        source: Position,
        target: Position,
    ) -> MoveResult:
        """
        Validates and schedules a move.
        """

        validation = self._rule_engine.validate_move(
            self._board,
            source,
            target,
        )

        if not validation.is_valid:
            return MoveResult.rejected(validation.reason)

        piece = self._board.get_piece(source)
        duration = self._duration_calculator.calculate(
            piece,
            source,
            target,
        )

        self._arbiter.start_motion(
            piece=piece,
            source=source,
            target=target,
            duration=duration,
        )

        return MoveResult.accepted()