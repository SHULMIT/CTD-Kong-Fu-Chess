"""
Manages the mutable game state.

Responsibilities:
    - Track whether the game has ended.
    - Advance the game simulation over time.
    - Update the game state after time-based events.
    - Delegate time-related actions to the RealTimeArbiter.

This service is responsible for game state transitions,
but it does not validate or execute chess moves.
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

    @property
    def current_time(self) -> int:
        """Returns the current simulation time in milliseconds."""
        return self._arbiter.current_time

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

    def get_active_motions(self) -> tuple:
        """Returns an immutable snapshot of all active motions."""
        return self._arbiter.get_active_motions()

    def jump_piece(
        self,
        piece: Piece,
    ) -> None:
        """
        Delegates piece jump to real-time arbiter.
        """

        self._arbiter.jump(piece)
