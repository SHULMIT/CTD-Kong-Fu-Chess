"""
Executes textual test commands.

Responsibilities:
    - Iterate over the input command list.
    - Parse each textual command.
    - Dispatch every command to the appropriate system component.
    - Delegate user actions to the Controller.
    - Delegate game-time operations to the GameEngine.
    - Print the board using the TextBoardFormatter.

This class does not implement game logic.
It only translates textual commands into method calls.
"""

from board_io.text_board_formatter import TextBoardFormatter
from config.constants import (
    COMMAND_CLICK,
    COMMAND_JUMP,
    COMMAND_PRINT_BOARD,
    COMMAND_WAIT,
)
from controller.controller import Controller
from errors.user_input_errors import EmptyCommandError, UnknownCommandError
from game.game_engine import GameEngine


class ScriptRunner:
    """
    Executes test commands.
    """

    def __init__(
        self,
        controller: Controller,
        game_engine: GameEngine,
    ):
        self._controller = controller
        self._game_engine = game_engine

    def run(
        self,
        commands: list[str],
    ) -> None:
        """
        Executes all commands.
        """

        for command in commands:

            command = command.strip()

            if not command:
                raise EmptyCommandError()

            if command.startswith(COMMAND_CLICK):
                self._handle_click(command)

            elif command.startswith(COMMAND_JUMP):
                self._handle_jump(command)

            elif command.startswith(COMMAND_WAIT):
                self._handle_wait(command)

            elif command == COMMAND_PRINT_BOARD:
                self._handle_print_board()
                
            else:
                raise UnknownCommandError()

    def _handle_click(
        self,
        command: str,
    ) -> None:
        """
        Executes a click command.
        """

        _, x, y = command.split()

        self._controller.handle_click(
            int(x),
            int(y),
        )

    def _handle_jump(
        self,
        command: str,
    ) -> None:
        """
        Executes a jump command.
        """

        _, x, y = command.split()

        self._controller.jump(
            int(x),
            int(y),
        )

    def _handle_wait(
        self,
        command: str,
    ) -> None:
        """
        Executes a wait command.
        """

        _, milliseconds = command.split()

        self._game_engine.wait(
            int(milliseconds),
        )

    def _handle_print_board(self) -> None:
        """
        Prints the current board.
        """

        print(
            TextBoardFormatter.format(
                self._game_engine.get_board()
            )
        )