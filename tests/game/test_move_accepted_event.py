"""Tests for move-acceptance event integration."""

from types import SimpleNamespace
from unittest.mock import MagicMock

from events.event_bus import EventBus
from events.game_events import MoveAcceptedEvent
from game.move_reason import MoveReason
from game.request_move_service import RequestMoveService
from model.position import Position


def _create_service(is_valid: bool) -> tuple[RequestMoveService, EventBus]:
    board = MagicMock()
    board.get_piece.return_value = MagicMock()
    rule_engine = MagicMock()
    rule_engine.validate_move.return_value = SimpleNamespace(
        is_valid=is_valid,
        reason=MoveReason.OK if is_valid else MoveReason.ILLEGAL_PIECE_MOVE,
    )
    duration_calculator = MagicMock()
    duration_calculator.calculate.return_value = 1000
    event_bus = EventBus()
    service = RequestMoveService(
        board=board,
        rule_engine=rule_engine,
        arbiter=MagicMock(),
        duration_calculator=duration_calculator,
        event_bus=event_bus,
    )
    return service, event_bus


def test_move_accepted_event_is_published_after_valid_move() -> None:
    service, event_bus = _create_service(is_valid=True)
    received: list[MoveAcceptedEvent] = []
    event_bus.subscribe(MoveAcceptedEvent, received.append)
    source = Position(6, 0)
    target = Position(5, 0)

    result = service.request_move(source, target)

    assert result.is_accepted
    assert received == [MoveAcceptedEvent(source=source, target=target)]


def test_move_accepted_event_is_not_published_after_rejected_move() -> None:
    service, event_bus = _create_service(is_valid=False)
    received: list[MoveAcceptedEvent] = []
    event_bus.subscribe(MoveAcceptedEvent, received.append)

    result = service.request_move(Position(6, 0), Position(3, 0))

    assert not result.is_accepted
    assert received == []
