"""Unit tests for external command parsing."""

from copy import deepcopy
from dataclasses import FrozenInstanceError

import pytest

from model.position import Position
from network.command_parser import CommandParser
from network.commands import JumpCommand, LegalMovesCommand, MoveCommand
from network.errors import CommandParseError


def test_parse_valid_move_command() -> None:
    message = {
        "type": "move",
        "source": {"row": 1, "column": 4},
        "target": {"row": 3, "column": 4},
    }

    command = CommandParser().parse(message)

    assert command == MoveCommand(
        source=Position(1, 4),
        target=Position(3, 4),
    )


def test_parse_valid_jump_command() -> None:
    message = {
        "type": "jump",
        "position": {"row": 2, "column": 3},
    }

    command = CommandParser().parse(message)

    assert command == JumpCommand(position=Position(2, 3))


def test_parse_valid_legal_moves_command() -> None:
    command = CommandParser().parse(
        {
            "type": "legal_moves",
            "position": {"row": 6, "column": 0},
        }
    )

    assert command == LegalMovesCommand(position=Position(6, 0))


def test_commands_are_immutable() -> None:
    command = JumpCommand(position=Position(2, 3))

    with pytest.raises(FrozenInstanceError):
        command.position = Position(0, 0)


def test_unknown_command_type_is_rejected() -> None:
    with pytest.raises(CommandParseError, match="Unknown command type"):
        CommandParser().parse({"type": "castle"})


@pytest.mark.parametrize(
    "message",
    [
        {"type": "move", "source": {"row": 1, "column": 2}},
        {"type": "jump"},
    ],
)
def test_missing_required_fields_are_rejected(
    message: dict[str, object],
) -> None:
    with pytest.raises(CommandParseError, match="Missing required field"):
        CommandParser().parse(message)


@pytest.mark.parametrize(
    "position",
    [
        None,
        [1, 2],
        {"row": 1},
        {"column": 2},
        {"row": 1, "column": 2, "depth": 0},
    ],
)
def test_malformed_positions_are_rejected(position: object) -> None:
    message = {"type": "jump", "position": position}

    with pytest.raises(CommandParseError):
        CommandParser().parse(message)


@pytest.mark.parametrize(
    "message",
    [
        {"type": 1, "position": {"row": 1, "column": 2}},
        {"type": "jump", "position": {"row": "1", "column": 2}},
        {"type": "jump", "position": {"row": 1, "column": 2.0}},
        {"type": "jump", "position": {"row": True, "column": 2}},
        {"type": "jump", "position": {1: 1, "column": 2}},
    ],
)
def test_incorrect_value_types_are_rejected(
    message: dict[str, object],
) -> None:
    with pytest.raises(CommandParseError):
        CommandParser().parse(message)


def test_parser_does_not_mutate_original_input() -> None:
    message = {
        "type": "move",
        "source": {"row": 1, "column": 4},
        "target": {"row": 3, "column": 4},
    }
    original = deepcopy(message)

    CommandParser().parse(message)

    assert message == original
