"""
Coordinates the game flow.
"""

from game.move_result import MoveReason, MoveResult
from model.board import Board
from model.position import Position
from realtime.duration_calculator import DurationCalculator
from realtime.real_time_arbiter import RealTimeArbiter
from rules.rule_engine import RuleEngine
from model.piece import Piece

class GameEngine:
	"""
	Coordinates the game.

	Responsible for:
	- validating moves
	- updating the board
	- tracking game state

	Does not implement chess rules.
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
		self._game_over = False

	@property
	def board(self) -> Board:
		return self._board

	@property
	def game_over(self) -> bool:
		return self._game_over

	def request_move(
		self,
		source: Position,
		target: Position,
	) -> MoveResult:
		"""
		Attempts to perform a move.
		"""

		if self._game_over:
			return MoveResult.rejected(
				MoveReason.GAME_OVER
			)

		if self._arbiter.has_active_motion():
			return MoveResult.rejected(
				MoveReason.MOTION_IN_PROGRESS
			)

		validation = self._rule_engine.validate_move(
			self._board,
			source,
			target,
		)

		if not validation.is_valid:
			return MoveResult.rejected(
				validation.reason
			)

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

	def wait(
		self,
		milliseconds: int,
	) -> None:
		self._arbiter.advance_time(milliseconds)

		if self._arbiter.consume_captured_king_flag():
			self._game_over = True

	def jump(
		self,
		position: Position,
	) -> None:
		"""
		Marks a piece as airborne.
		"""

		piece = self._board.get_piece(position)

		if not isinstance(piece, Piece):
			return

		self._arbiter.jump(piece)

	def is_inside(self, position: Position) -> bool:
		return self._board.is_inside(position)

	def get_piece(self, position: Position):
		return self._board.get_piece(position)

	def has_piece(self, position: Position) -> bool:
		piece = self._board.get_piece(position)
		return piece is not None and piece != self._board.EMPTY_CELL

	def get_board(self) -> Board:
		return self._board
         