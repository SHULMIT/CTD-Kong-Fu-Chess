"""
Coordinates the game flow.

Responsibilities:
    - Expose a stable API to the rest of the application.
    - Coordinate game services.
    - Delegate move requests to the RequestMoveService.
    - Delegate game state operations to the GameStateService.
    - Delegate board queries to the GameQueryService.

This class does not implement chess rules or movement logic.
It acts as the central facade of the game layer.
"""

from game.move_result import MoveReason, MoveResult
from game.player_activity_service import PlayerActivityService
from game.game_query_service import GameQueryService
from game.game_state_service import GameStateService
from game.request_move_service import RequestMoveService
from errors.user_input_errors import JumpEmptySourceError
from model.board import Board
from model.position import Position
from realtime.duration_calculator import DurationCalculator
from realtime.real_time_arbiter import RealTimeArbiter
from rules.rule_engine import RuleEngine
from model.piece import Piece, PieceColor, PieceType

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
		player_activity: PlayerActivityService | None = None,
	):
		self._player_activity = player_activity or PlayerActivityService()
		arbiter.set_player_activity(self._player_activity)
		self._query_service = GameQueryService(board)
		self._state_service = GameStateService(arbiter)
		self._request_move_service = RequestMoveService(
			board=board,
			rule_engine=rule_engine,
			arbiter=arbiter,
			duration_calculator=duration_calculator,
			player_activity=self._player_activity,
		)

	@property
	def board(self) -> Board:
		return self._query_service.board

	@property
	def game_over(self) -> bool:
		return self._state_service.game_over

	@property
	def player_activity(self) -> PlayerActivityService:
		"""Returns the action and score data for the current game."""
		return self._player_activity

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
		self._player_activity.record_jump(
			player=piece.color,
			piece_type=piece.type,
			position=position,
			timestamp_milliseconds=self._state_service.current_time,
		)

	def is_inside(self, position: Position) -> bool:
		return self._query_service.is_inside(position)

	def get_piece(self, position: Position) -> object | None:
		return self._query_service.get_piece(position)

	def has_piece(self, position: Position) -> bool:
		return self._query_service.has_piece(position)

	def get_legal_moves(
		self,
		source: Position,
	) -> set[Position]:
		"""
		Returns all legal destination positions for the piece at source.
		Used by the UI to display legal move indicators.
		"""
		return self._request_move_service.get_legal_moves(source)

	def get_motions(self) -> tuple:
		"""
		Returns an immutable snapshot of all active motions for UI interpolation.
		"""
		return self._state_service.get_active_motions()

	def get_winner(self) -> PieceColor | None:
		"""Returns the color whose king remains on the board, if any."""
		white_king_alive = self._has_king(PieceColor.WHITE)
		black_king_alive = self._has_king(PieceColor.BLACK)

		if white_king_alive and not black_king_alive:
			return PieceColor.WHITE
		if black_king_alive and not white_king_alive:
			return PieceColor.BLACK
		return None

	def get_board(self) -> Board:
		return self._query_service.board

	def _has_king(self, color: PieceColor) -> bool:
		"""Checks the current board without exposing winner-resolution details."""
		board = self._query_service.board
		for row in range(board.height):
			for column in range(board.width):
				piece = board.get_piece(Position(row, column))
				if (
					isinstance(piece, Piece)
					and piece.type == PieceType.KING
					and piece.color == color
				):
					return True
		return False
