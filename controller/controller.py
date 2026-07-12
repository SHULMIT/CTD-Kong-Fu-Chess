"""
Translates user clicks into game commands.
"""

from controller.board_mapper import BoardMapper
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
            return

        if self._selected_position is None:
            if not self._game_engine.has_piece(position):
                return

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

        self._game_engine.request_move(
            self._selected_position,
            position,
        )

        self._selected_position = None

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
            return

        self._game_engine.jump(position)