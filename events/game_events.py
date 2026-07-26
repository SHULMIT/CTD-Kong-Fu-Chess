"""Immutable events emitted by the game layer."""

from dataclasses import dataclass

from events.event import Event
from model.piece import PieceColor
from model.position import Position


@dataclass(frozen=True)
class GameStartedEvent(Event):
    """Reports that a game has started.

    מייצגת את רכיב השרת ``GameStartedEvent`` ומרכזת את התנהגותו.

    Responsibility: Reports that a game has started.

    אחריות: מייצגת את רכיב השרת ``GameStartedEvent`` ומרכזת את התנהגותו."""


@dataclass(frozen=True)
class MoveAcceptedEvent(Event):
    """Reports the source and target of a successfully accepted move.

    מייצגת את רכיב השרת ``MoveAcceptedEvent`` ומרכזת את התנהגותו.

    Responsibility: Reports the source and target of a successfully accepted move.

    אחריות: מייצגת את רכיב השרת ``MoveAcceptedEvent`` ומרכזת את התנהגותו."""

    source: Position
    target: Position


@dataclass(frozen=True)
class MoveStartedEvent(Event):
    """Reports that a piece has begun moving between two positions.

    מייצגת את רכיב השרת ``MoveStartedEvent`` ומרכזת את התנהגותו.

    Responsibility: Reports that a piece has begun moving between two positions.

    אחריות: מייצגת את רכיב השרת ``MoveStartedEvent`` ומרכזת את התנהגותו."""

    piece_id: int
    source: Position
    target: Position


@dataclass(frozen=True)
class MoveCompletedEvent(Event):
    """Reports that a piece has completed a movement.

    מייצגת את רכיב השרת ``MoveCompletedEvent`` ומרכזת את התנהגותו.

    Responsibility: Reports that a piece has completed a movement.

    אחריות: מייצגת את רכיב השרת ``MoveCompletedEvent`` ומרכזת את התנהגותו."""

    piece_id: int
    source: Position
    target: Position


@dataclass(frozen=True)
class JumpStartedEvent(Event):
    """Reports that a piece has started jumping at its current position.

    מייצגת את רכיב השרת ``JumpStartedEvent`` ומרכזת את התנהגותו.

    Responsibility: Reports that a piece has started jumping at its current position.

    אחריות: מייצגת את רכיב השרת ``JumpStartedEvent`` ומרכזת את התנהגותו."""

    piece_id: int
    position: Position


@dataclass(frozen=True)
class JumpCompletedEvent(Event):
    """Reports that a piece has completed a jump at its current position.

    מייצגת את רכיב השרת ``JumpCompletedEvent`` ומרכזת את התנהגותו.

    Responsibility: Reports that a piece has completed a jump at its current position.

    אחריות: מייצגת את רכיב השרת ``JumpCompletedEvent`` ומרכזת את התנהגותו."""

    piece_id: int
    position: Position


@dataclass(frozen=True)
class ScoreChangedEvent(Event):
    """Reports a player's new accumulated capture score.

    מייצגת את רכיב השרת ``ScoreChangedEvent`` ומרכזת את התנהגותו.

    Responsibility: Reports a player's new accumulated capture score.

    אחריות: מייצגת את רכיב השרת ``ScoreChangedEvent`` ומרכזת את התנהגותו."""

    player: PieceColor
    score: int


@dataclass(frozen=True)
class GameOverEvent(Event):
    """Reports that a game has ended and identifies its winner, if any.

    מייצגת את רכיב השרת ``GameOverEvent`` ומרכזת את התנהגותו.

    Responsibility: Reports that a game has ended and identifies its winner, if any.

    אחריות: מייצגת את רכיב השרת ``GameOverEvent`` ומרכזת את התנהגותו."""

    winner: PieceColor | None
