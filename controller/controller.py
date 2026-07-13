
"""
Translates user input into game commands.

Responsibilities:
    - Receive user input events.
    - Convert screen coordinates into board positions.
    - Manage the currently selected piece.
    - Interpret user clicks as selection or movement requests.
    - Delegate game actions to the GameEngine.

This class does not implement chess rules.
It only translates user interactions into game requests.
"""

from controller.board_mapper import BoardMapper
from errors.user_input_errors import (
    ClickEmptySourceError,
    ClickOutsideBoardError,
    JumpEmptySourceError,
    JumpOutsideBoardError,
    raise_for_move_reason,
)
from game.game_engine import GameEngine
from model.position import Position


class Controller:
    """
    Handles user input.
    """

    def __init__(
        self,
        game_engine: GameEngine,
        board_mapper: BoardMapper,
    ):
        self._game_engine = game_engine
        self._board_mapper = board_mapper
        self._selected_position: Position | None = None

    def handle_click(
        self,
        x: int,
        y: int,
    ) -> None:
        """
        Handles a mouse click.
        """

        position = self._board_mapper.to_position(
            x,
            y,
        )

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

    def jump(
        self,
        x: int,
        y: int,
    ) -> None:
        """
        Marks the clicked piece as airborne.
        """

        position = self._board_mapper.to_position(
            x,
            y,
        )

        if not self._game_engine.is_inside(position):
            raise JumpOutsideBoardError()

        if not self._game_engine.has_piece(position):
            raise JumpEmptySourceError()

        self._game_engine.jump(position)