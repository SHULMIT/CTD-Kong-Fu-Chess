"""
controller.py

Translates user input into game commands.

Responsibilities:
    - Receive board positions from the UI layer.
    - Manage the currently selected piece.
    - Interpret clicks as selection or movement requests.
    - Delegate game actions to the GameEngine.

This class does not know about pixels, screen coordinates, or UI layout.
It works exclusively with board Position objects.
"""

from errors.user_input_errors import (
    ClickEmptySourceError,
    ClickOutsideBoardError,
    raise_for_move_reason,
)
from game.game_engine import GameEngine
from model.position import Position


class Controller:
    """
    Handles board-level user input.
    """

    def __init__(
        self,
        game_engine: GameEngine,
    ):
        self._game_engine = game_engine
        self._selected_position: Position | None = None

    @property
    def selected_position(self) -> Position | None:
        return self._selected_position

    def handle_position(
        self,
        position: Position,
    ) -> None:
        """
        Handles a board position click.

        First click selects a piece.
        Second click attempts to move the selected piece to the target.
        """

        if not self._game_engine.is_inside(position):
            self._selected_position = None
            raise ClickOutsideBoardError()

        if self._selected_position is None:
            if not self._game_engine.has_piece(position):
                raise ClickEmptySourceError()

            self._selected_position = position
            return

        if self._game_engine.has_piece(position):
            selected_piece = self._game_engine.get_piece(
                self._selected_position
            )
            target_piece = self._game_engine.get_piece(position)

            if selected_piece.color == target_piece.color:
                self._selected_position = position
                return

        result = self._game_engine.request_move(
            self._selected_position,
            position,
        )

        self._selected_position = None

        if not result.is_accepted:
            raise_for_move_reason(result.reason)

    def jump_at(
        self,
        position: Position,
    ) -> None:
        """
        Marks the piece at the given board position as airborne.

        The caller (UI layer) is responsible for converting pixel
        coordinates to a Position before calling this method.
        """

        self._game_engine.jump(position)

    def deselect(self) -> None:
        """Clears the current selection."""
        self._selected_position = None
