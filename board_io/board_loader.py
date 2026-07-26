from pathlib import Path

from board_io.text_board_parser import TextBoardParser
from model.board import Board


class BoardLoader:
    """Loads a board from a text file.

        Responsibilities:
            - Read a board file.
            - Parse it into a Board object.

    מייצגת את רכיב השרת ``BoardLoader`` ומרכזת את התנהגותו.

    Responsibility: Loads a board from a text file.

    אחריות: מייצגת את רכיב השרת ``BoardLoader`` ומרכזת את התנהגותו."""

    @staticmethod
    def load(
        path: str | Path,
    ) -> Board:

        """Perform the load operation.

        מבצעת את פעולת ``load``."""
        with open(
            path,
            encoding="utf-8",
        ) as file:

            board_lines = file.read().splitlines()

        return TextBoardParser.parse(
            board_lines
        )