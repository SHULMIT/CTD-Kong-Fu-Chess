"""
Manages mutable game state that is independent from move validation.
"""

from model.piece import Piece
from realtime.real_time_arbiter import RealTimeArbiter


class GameStateService:
    """
    Owns game-over state and time-based state transitions.
    """

    def __init__(
        self,
        arbiter: RealTimeArbiter,
    ):
        self._arbiter = arbiter
        self._game_over = False

    @property
    def game_over(self) -> bool:
        """
        Returns whether the game has ended.
        """

        return self._game_over

    def mark_game_over(self) -> None:
        """
        Marks game as ended.
        """

        self._game_over = True

    def wait(
        self,
        milliseconds: int,
    ) -> None:
        """
        Advances simulation and updates game-over state.
        """

        self._arbiter.advance_time(milliseconds)

        if self._arbiter.consume_captured_king_flag():
            self._game_over = True

    def jump_piece(
        self,
        piece: Piece,
    ) -> None:
        """
        Delegates piece jump to real-time arbiter.
        """

        self._arbiter.jump(piece)