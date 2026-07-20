"""Immutable events emitted by the game layer."""

from dataclasses import dataclass

from events.event import Event
from model.piece import PieceColor
from model.position import Position


@dataclass(frozen=True)
class GameStartedEvent(Event):
    """Reports that a game has started."""


@dataclass(frozen=True)
class MoveAcceptedEvent(Event):
    """Reports the source and target of a successfully accepted move."""

    source: Position
    target: Position


@dataclass(frozen=True)
class MoveStartedEvent(Event):
    """Reports that a piece has begun moving between two positions."""

    piece_id: int
    source: Position
    target: Position


@dataclass(frozen=True)
class MoveCompletedEvent(Event):
    """Reports that a piece has completed a movement."""

    piece_id: int
    source: Position
    target: Position


@dataclass(frozen=True)
class JumpStartedEvent(Event):
    """Reports that a piece has started jumping at its current position."""

    piece_id: int
    position: Position


@dataclass(frozen=True)
class JumpCompletedEvent(Event):
    """Reports that a piece has completed a jump at its current position."""

    piece_id: int
    position: Position


@dataclass(frozen=True)
class ScoreChangedEvent(Event):
    """Reports a player's new accumulated capture score."""

    player: PieceColor
    score: int


@dataclass(frozen=True)
class GameOverEvent(Event):
    """Reports that a game has ended and identifies its winner, if any."""

    winner: PieceColor | None
