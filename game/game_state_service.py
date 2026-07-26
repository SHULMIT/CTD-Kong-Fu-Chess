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
    """Owns game-over state and time-based state transitions.

    מייצגת את רכיב השרת ``GameStateService`` ומרכזת את התנהגותו.

    Responsibility: Owns game-over state and time-based state transitions.

    אחריות: מייצגת את רכיב השרת ``GameStateService`` ומרכזת את התנהגותו."""

    def __init__(
        self,
        arbiter: RealTimeArbiter,
    ):
        """Initialize the instance and its dependencies.

        מאתחלת את המופע ואת התלויות שלו."""
        self._arbiter = arbiter
        self._game_over = False

    @property
    def game_over(self) -> bool:
        """Returns whether the game has ended.

        מבצעת את פעולת המשחק ``over``."""

        return self._game_over

    @property
    def current_time(self) -> int:
        """Returns the current simulation time in milliseconds.

        מבצעת את פעולת ``current`` הזמן."""
        return self._arbiter.current_time

    def mark_game_over(self) -> None:
        """Marks game as ended.

        מבצעת את פעולת ``mark`` המשחק ``over``."""

        self._game_over = True

    def wait(
        self,
        milliseconds: int,
    ) -> None:
        """Advances simulation and updates game-over state.

        מבצעת את פעולת ``wait``."""

        self._arbiter.advance_time(milliseconds)

        if self._arbiter.consume_captured_king_flag():
            self._game_over = True

    def get_active_motions(self) -> tuple:
        """Returns an immutable snapshot of all active motions.

        מחזירה את ``active`` ``motions``."""
        return self._arbiter.get_active_motions()

    def jump_piece(
        self,
        piece: Piece,
    ) -> None:
        """Delegates piece jump to real-time arbiter.

        מבצעת את פעולת קפיצה הכלי."""

        self._arbiter.jump(piece)
