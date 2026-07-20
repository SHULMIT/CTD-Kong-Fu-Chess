"""Immutable commands accepted at the external game boundary."""

from dataclasses import dataclass

from model.position import Position


@dataclass(frozen=True)
class MoveCommand:
    """Requests movement from one board position to another."""

    source: Position
    target: Position


@dataclass(frozen=True)
class JumpCommand:
    """Requests a jump for the piece at a board position."""

    position: Position


@dataclass(frozen=True)
class LegalMovesCommand:
    """Requests legal destinations for the piece at a board position."""

    position: Position


NetworkCommand = MoveCommand | JumpCommand | LegalMovesCommand
