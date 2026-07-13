"""
Coordinates the game flow.
"""

from game.move_result import MoveReason, MoveResult
from game.game_query_service import GameQueryService
from game.game_state_service import GameStateService
from game.request_move_service import RequestMoveService
from errors.user_input_errors import JumpEmptySourceError
from model.board import Board
from model.position import Position
from realtime.duration_calculator import DurationCalculator
from realtime.real_time_arbiter import RealTimeArbiter
from rules.rule_engine import RuleEngine
from model.piece import Piece

class GameEngine:
	"""
	Coordinates game services and exposes a stable facade API.
	"""

	def __init__(
		self,
		board: Board,
		rule_engine: RuleEngine,
		arbiter: RealTimeArbiter,
		duration_calculator: DurationCalculator,
	):
		self._query_service = GameQueryService(board)
		self._state_service = GameStateService(arbiter)
		self._request_move_service = RequestMoveService(
			board=board,
			rule_engine=rule_engine,
			arbiter=arbiter,
			duration_calculator=duration_calculator,
		)

	@property
	def board(self) -> Board:
		return self._query_service.board

	@property
	def game_over(self) -> bool:
		return self._state_service.game_over

	def request_move(
		self,
		source: Position,
		target: Position,
	) -> MoveResult:
		"""
		Attempts to perform a move.
		"""

		if self.game_over:
			return MoveResult.rejected(
				MoveReason.GAME_OVER
			)

		return self._request_move_service.request_move(
			source=source,
			target=target,
		)

	def wait(
		self,
		milliseconds: int,
	) -> None:
		self._state_service.wait(milliseconds)

	def jump(
		self,
		position: Position,
	) -> None:
		"""
		Marks a piece as airborne.
		"""

		piece = self._query_service.get_piece(position)

		if not isinstance(piece, Piece):
			raise JumpEmptySourceError()

		self._state_service.jump_piece(piece)

	def is_inside(self, position: Position) -> bool:
		return self._query_service.is_inside(position)

	def get_piece(self, position: Position) -> object | None:
		return self._query_service.get_piece(position)

	def has_piece(self, position: Position) -> bool:
		return self._query_service.has_piece(position)

	def get_board(self) -> Board:
		return self._query_service.board
         