"""Tests for the shared game-event wire protocol."""

import json

import pytest

from events.event import Event
from events.game_events import (
    GameOverEvent,
    JumpCompletedEvent,
    JumpStartedEvent,
    MoveCompletedEvent,
    MoveStartedEvent,
    ScoreChangedEvent,
)
from model.piece import PieceColor
from model.position import Position
from network.game_event_type import GameEventType
from network.server.transport.game_event_serializer import GameEventSerializer


SOURCE = Position(6, 0)
TARGET = Position(5, 0)


@pytest.mark.parametrize(
    ("event", "event_type"),
    [
        (
            MoveStartedEvent(piece_id=1, source=SOURCE, target=TARGET),
            GameEventType.MOVE_STARTED,
        ),
        (
            MoveCompletedEvent(piece_id=1, source=SOURCE, target=TARGET),
            GameEventType.MOVE_COMPLETED,
        ),
        (JumpStartedEvent(piece_id=1, position=SOURCE), GameEventType.JUMP_STARTED),
        (
            JumpCompletedEvent(piece_id=1, position=SOURCE),
            GameEventType.JUMP_COMPLETED,
        ),
        (
            ScoreChangedEvent(player=PieceColor.WHITE, score=5),
            GameEventType.SCORE_CHANGED,
        ),
        (GameOverEvent(winner=PieceColor.WHITE), GameEventType.GAME_OVER),
    ],
)
def test_serializer_uses_shared_json_string_discriminator(
    event: Event,
    event_type: GameEventType,
) -> None:
    payload = GameEventSerializer().serialize(event)

    assert payload["type"] == event_type.value
    assert json.loads(json.dumps(payload))["type"] == event_type.value
