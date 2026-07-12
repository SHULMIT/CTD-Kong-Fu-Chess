"""
Program entry point.
"""

import sys

from board_io.text_board_parser import TextBoardParser
from controller.board_mapper import BoardMapper
from controller.controller import Controller
from game.game_engine import GameEngine
from realtime.duration_calculator import DurationCalculator
from realtime.real_time_arbiter import RealTimeArbiter
from rules.rule_engine import RuleEngine
from runner.script_runner import ScriptRunner


def _split_input(
    lines: list[str],
) -> tuple[list[str], list[str]]:
    """
    Splits the input into board lines and command lines.
    """

    board_lines = []
    command_lines = []

    current_section = None

    for line in lines:

        line = line.strip()

        if line == "Board:":
            current_section = board_lines
            continue

        if line == "Commands:":
            current_section = command_lines
            continue

        if current_section is not None:
            current_section.append(line)

    return board_lines, command_lines


def main() -> None:
    """
    Program entry point.
    """

    lines = sys.stdin.read().splitlines()

    board_lines, command_lines = _split_input(lines)

    try:
        board = TextBoardParser.parse(board_lines)

    except ValueError as error:
        print(error)
        return

    rule_engine = RuleEngine()

    arbiter = RealTimeArbiter(board)

    duration_calculator = DurationCalculator()

    game_engine = GameEngine(
        board=board,
        rule_engine=rule_engine,
        arbiter=arbiter,
        duration_calculator=duration_calculator,
    )

    board_mapper = BoardMapper()

    controller = Controller(
        game_engine=game_engine,
        board_mapper=board_mapper,
    )

    runner = ScriptRunner(
        controller=controller,
        game_engine=game_engine,
    )

    runner.run(command_lines)


if __name__ == "__main__":
    main()