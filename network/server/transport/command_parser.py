"""Validation and conversion of external dictionaries into commands."""

from network.server.transport.commands import (
    JumpCommand,
    LegalMovesCommand,
    MoveCommand,
    NetworkCommand,
)
from network.server.transport.errors import CommandParseError
from model.position import Position


class CommandParser:
    """Converts validated external message data into domain commands."""

    def parse(self, message: dict[str, object]) -> NetworkCommand:
        """Return the command represented by ``message``.

        This validates only message shape and primitive value types. Chess
        legality remains the responsibility of the game rules.
        """
        if not isinstance(message, dict):
            raise CommandParseError("Command must be a dictionary.")

        command_type = message.get("type")
        if not isinstance(command_type, str):
            raise CommandParseError("Command type must be a string.")

        if command_type == "move":
            return self._parse_move(message)
        if command_type == "jump":
            return self._parse_jump(message)
        if command_type == "legal_moves":
            return self._parse_legal_moves(message)
        raise CommandParseError(f"Unknown command type: {command_type!r}.")

    def _parse_move(self, message: dict[str, object]) -> MoveCommand:
        self._require_fields(message, {"type", "source", "target"})
        return MoveCommand(
            source=self._parse_position(message["source"], "source"),
            target=self._parse_position(message["target"], "target"),
        )

    def _parse_jump(self, message: dict[str, object]) -> JumpCommand:
        self._require_fields(message, {"type", "position"})
        return JumpCommand(
            position=self._parse_position(message["position"], "position")
        )

    def _parse_legal_moves(
        self,
        message: dict[str, object],
    ) -> LegalMovesCommand:
        self._require_fields(message, {"type", "position"})
        return LegalMovesCommand(
            position=self._parse_position(message["position"], "position")
        )

    @staticmethod
    def _require_fields(
        message: dict[str, object],
        expected_fields: set[str],
    ) -> None:
        if not all(isinstance(field, str) for field in message):
            raise CommandParseError("Command field names must be strings.")

        actual_fields = set(message)
        missing_fields = expected_fields - actual_fields
        if missing_fields:
            missing = ", ".join(sorted(missing_fields))
            raise CommandParseError(f"Missing required field(s): {missing}.")

        unexpected_fields = actual_fields - expected_fields
        if unexpected_fields:
            unexpected = ", ".join(sorted(unexpected_fields))
            raise CommandParseError(f"Unexpected field(s): {unexpected}.")

    @staticmethod
    def _parse_position(value: object, field_name: str) -> Position:
        if not isinstance(value, dict):
            raise CommandParseError(f"{field_name} must be a dictionary.")
        if not all(isinstance(field, str) for field in value):
            raise CommandParseError(
                f"{field_name} field names must be strings."
            )
        if set(value) != {"row", "column"}:
            raise CommandParseError(
                f"{field_name} must contain only row and column."
            )

        row = value["row"]
        column = value["column"]
        if type(row) is not int or type(column) is not int:
            raise CommandParseError(
                f"{field_name} row and column must be integers."
            )
        return Position(row=row, column=column)
