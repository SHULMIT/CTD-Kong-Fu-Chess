"""
Executes textual test commands.
"""

from board_io.text_board_formatter import TextBoardFormatter
from controller.controller import Controller
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
                continue

            if command.startswith("click"):
                self._handle_click(command)

            elif command.startswith("jump"):
                self._handle_jump(command)

            elif command.startswith("wait"):
                self._handle_wait(command)

            elif command == "print board":
                self._handle_print_board()

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