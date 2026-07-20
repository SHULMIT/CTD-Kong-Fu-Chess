"""Tests for independent game-domain composition."""

from app.game_engine_factory import GameEngineFactory
from events.game_events import MoveAcceptedEvent
from model.piece import PieceColor
from model.position import Position


def test_create_returns_games_with_independent_mutable_state() -> None:
    first_engine = GameEngineFactory.create()
    second_engine = GameEngineFactory.create()
    source = Position(6, 0)
    target = Position(5, 0)

    assert first_engine is not second_engine
    assert first_engine.board is not second_engine.board
    assert first_engine.player_activity is not second_engine.player_activity
    assert first_engine.get_piece(source) is not second_engine.get_piece(source)

    result = first_engine.request_move(source, target)

    assert result.is_accepted
    assert first_engine.get_motions()
    assert second_engine.get_motions() == ()
    assert len(first_engine.player_activity.get_actions(PieceColor.WHITE)) == 1
    assert second_engine.player_activity.get_actions(PieceColor.WHITE) == ()
    assert second_engine.has_piece(source)
    assert not second_engine.has_piece(target)


def test_created_games_do_not_share_events() -> None:
    first_engine = GameEngineFactory.create()
    second_engine = GameEngineFactory.create()
    first_events: list[MoveAcceptedEvent] = []
    second_events: list[MoveAcceptedEvent] = []
    first_engine.event_bus.subscribe(MoveAcceptedEvent, first_events.append)
    second_engine.event_bus.subscribe(MoveAcceptedEvent, second_events.append)

    result = first_engine.request_move(Position(6, 0), Position(5, 0))

    assert result.is_accepted
    assert first_events == [
        MoveAcceptedEvent(source=Position(6, 0), target=Position(5, 0))
    ]
    assert second_events == []
