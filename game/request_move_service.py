
"""
Processes move requests.

Responsibilities:
    - Validate requested moves.
    - Calculate movement duration.
    - Schedule legal piece motions.
    - Return the outcome of the move request.

This service is responsible only for processing move requests.
It does not manage the game state or implement chess rules.
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

    def get_legal_moves(
        self,
        source: Position,
    ) -> set[Position]:
        """
        Returns all legal destination positions for the piece at source.
        """
        from model.piece import Piece
        piece = self._board.get_piece(source)
        if not isinstance(piece, Piece):
            return set()
        return self._rule_engine.get_legal_moves(self._board, piece)

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