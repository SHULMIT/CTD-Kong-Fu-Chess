"""Unit tests for immutable game-domain event data objects."""

from dataclasses import FrozenInstanceError, is_dataclass

import pytest

from events.event import Event
from events.game_events import (
    GameOverEvent,
    GameStartedEvent,
    JumpCompletedEvent,
    JumpStartedEvent,
    MoveCompletedEvent,
    MoveStartedEvent,
    ScoreChangedEvent,
)
from model.piece import PieceColor
from model.position import Position


SOURCE = Position(6, 0)
TARGET = Position(5, 0)


@pytest.mark.parametrize(
    "event",
    [
        GameStartedEvent(),
        MoveStartedEvent(piece_id=1, source=SOURCE, target=TARGET),
        MoveCompletedEvent(piece_id=1, source=SOURCE, target=TARGET),
        JumpStartedEvent(piece_id=2, position=SOURCE),
        JumpCompletedEvent(piece_id=2, position=SOURCE),
        ScoreChangedEvent(player=PieceColor.WHITE, score=5),
        GameOverEvent(winner=PieceColor.BLACK),
    ],
    ids=lambda event: type(event).__name__,
)
def test_game_event_is_an_immutable_event(event: Event) -> None:
    assert isinstance(event, Event)
    assert is_dataclass(event)

    with pytest.raises(FrozenInstanceError):
        event.unexpected_value = "changed"  # type: ignore[attr-defined]


def test_game_started_event_contains_no_unnecessary_data() -> None:
    assert GameStartedEvent().__dict__ == {}


@pytest.mark.parametrize(
    "event_type",
    [MoveStartedEvent, MoveCompletedEvent],
)
def test_move_event_contains_piece_and_route(event_type: type[Event]) -> None:
    event = event_type(piece_id=7, source=SOURCE, target=TARGET)

    assert event.piece_id == 7
    assert event.source is SOURCE
    assert event.target is TARGET


@pytest.mark.parametrize(
    "event_type",
    [JumpStartedEvent, JumpCompletedEvent],
)
def test_jump_event_contains_piece_and_position(event_type: type[Event]) -> None:
    event = event_type(piece_id=4, position=TARGET)

    assert event.piece_id == 4
    assert event.position is TARGET


def test_score_changed_event_contains_player_and_new_score() -> None:
    event = ScoreChangedEvent(player=PieceColor.WHITE, score=9)

    assert event.player is PieceColor.WHITE
    assert event.score == 9


@pytest.mark.parametrize("winner", [PieceColor.WHITE, PieceColor.BLACK, None])
def test_game_over_event_supports_winner_or_no_winner(
    winner: PieceColor | None,
) -> None:
    assert GameOverEvent(winner=winner).winner is winner
