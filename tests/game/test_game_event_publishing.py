"""Integration tests for domain events published by the game flow."""

from types import SimpleNamespace
from unittest.mock import MagicMock

from config.constants import EMPTY_SQUARE, JUMP_DURATION_MILLISECONDS
from events.event import Event
from events.event_bus import EventBus
from events.game_events import (
    GameOverEvent,
    GameStartedEvent,
    JumpCompletedEvent,
    JumpStartedEvent,
    MoveAcceptedEvent,
    MoveCompletedEvent,
    MoveStartedEvent,
    ScoreChangedEvent,
)
from game.game_engine import GameEngine
from game.move_reason import MoveReason
from model.board import Board
from model.piece import Piece, PieceColor, PieceType
from model.position import Position
from realtime.duration_calculator import DurationCalculator
from realtime.real_time_arbiter import RealTimeArbiter


def _piece(
    piece_id: int,
    piece_type: PieceType,
    color: PieceColor,
    position: Position,
) -> Piece:
    return Piece(piece_id, piece_type, color, position)


def _engine(
    board: Board,
    event_bus: EventBus,
    move_is_valid: bool = True,
    duration: int = 100,
) -> GameEngine:
    rule_engine = MagicMock()
    rule_engine.validate_move.return_value = SimpleNamespace(
        is_valid=move_is_valid,
        reason=(
            MoveReason.OK
            if move_is_valid
            else MoveReason.ILLEGAL_PIECE_MOVE
        ),
    )
    duration_calculator = MagicMock(spec=DurationCalculator)
    duration_calculator.calculate.return_value = duration
    arbiter = RealTimeArbiter(board)
    return GameEngine(
        board=board,
        rule_engine=rule_engine,
        arbiter=arbiter,
        duration_calculator=duration_calculator,
        event_bus=event_bus,
    )


def test_game_started_event_is_published_once_after_initialization() -> None:
    event_bus = EventBus()
    events: list[GameStartedEvent] = []
    event_bus.subscribe(GameStartedEvent, events.append)

    _engine(Board([[EMPTY_SQUARE]]), event_bus)

    assert events == [GameStartedEvent()]


def test_legal_move_publishes_each_move_event_once() -> None:
    source = Position(0, 0)
    target = Position(0, 1)
    mover = _piece(1, PieceType.ROOK, PieceColor.WHITE, source)
    event_bus = EventBus()
    engine = _engine(Board([[mover, EMPTY_SQUARE]]), event_bus)
    started: list[MoveStartedEvent] = []
    accepted: list[MoveAcceptedEvent] = []
    completed: list[MoveCompletedEvent] = []
    event_bus.subscribe(MoveStartedEvent, started.append)
    event_bus.subscribe(MoveAcceptedEvent, accepted.append)
    event_bus.subscribe(MoveCompletedEvent, completed.append)

    result = engine.request_move(source, target)
    engine.wait(100)
    engine.wait(100)

    assert result.is_accepted
    assert started == [MoveStartedEvent(1, source, target)]
    assert accepted == [MoveAcceptedEvent(source, target)]
    assert completed == [MoveCompletedEvent(1, source, target)]
    assert engine.get_piece(target) is mover


def test_invalid_move_publishes_no_gameplay_events() -> None:
    source = Position(0, 0)
    mover = _piece(1, PieceType.ROOK, PieceColor.WHITE, source)
    event_bus = EventBus()
    engine = _engine(
        Board([[mover, EMPTY_SQUARE]]),
        event_bus,
        move_is_valid=False,
    )
    events: list[Event] = []
    gameplay_event_types = (
        MoveStartedEvent,
        MoveAcceptedEvent,
        MoveCompletedEvent,
        ScoreChangedEvent,
        GameOverEvent,
    )
    for event_type in gameplay_event_types:
        event_bus.subscribe(event_type, events.append)

    result = engine.request_move(source, Position(0, 1))

    assert not result.is_accepted
    assert events == []
    assert engine.get_piece(source) is mover


def test_jump_publishes_started_and_completed_once() -> None:
    position = Position(0, 0)
    jumper = _piece(3, PieceType.KNIGHT, PieceColor.WHITE, position)
    event_bus = EventBus()
    engine = _engine(Board([[jumper]]), event_bus)
    started: list[JumpStartedEvent] = []
    completed: list[JumpCompletedEvent] = []
    event_bus.subscribe(JumpStartedEvent, started.append)
    event_bus.subscribe(JumpCompletedEvent, completed.append)

    engine.jump(position)
    engine.wait(JUMP_DURATION_MILLISECONDS)
    engine.wait(JUMP_DURATION_MILLISECONDS)

    assert started == [JumpStartedEvent(3, position)]
    assert completed == [JumpCompletedEvent(3, position)]


def test_score_changed_is_published_only_when_capture_changes_score() -> None:
    source = Position(0, 0)
    target = Position(0, 1)
    attacker = _piece(1, PieceType.ROOK, PieceColor.WHITE, source)
    queen = _piece(2, PieceType.QUEEN, PieceColor.BLACK, target)
    event_bus = EventBus()
    engine = _engine(Board([[attacker, queen]]), event_bus)
    events: list[ScoreChangedEvent] = []
    event_bus.subscribe(ScoreChangedEvent, events.append)

    engine.request_move(source, target)
    engine.wait(100)
    engine.wait(100)

    assert events == [ScoreChangedEvent(PieceColor.WHITE, 9)]
    assert engine.player_activity.get_score(PieceColor.WHITE) == 9


def test_zero_point_capture_does_not_publish_score_changed() -> None:
    source = Position(0, 0)
    target = Position(0, 1)
    attacker = _piece(1, PieceType.ROOK, PieceColor.WHITE, source)
    king = _piece(2, PieceType.KING, PieceColor.BLACK, target)
    event_bus = EventBus()
    engine = _engine(Board([[attacker, king]]), event_bus)
    events: list[ScoreChangedEvent] = []
    event_bus.subscribe(ScoreChangedEvent, events.append)

    engine.request_move(source, target)
    engine.wait(100)

    assert events == []
    assert engine.player_activity.get_score(PieceColor.WHITE) == 0


def test_game_over_is_published_once_when_king_is_captured() -> None:
    king_position = Position(0, 0)
    source = Position(0, 1)
    target = Position(0, 2)
    white_king = _piece(1, PieceType.KING, PieceColor.WHITE, king_position)
    attacker = _piece(2, PieceType.ROOK, PieceColor.WHITE, source)
    black_king = _piece(3, PieceType.KING, PieceColor.BLACK, target)
    event_bus = EventBus()
    engine = _engine(Board([[white_king, attacker, black_king]]), event_bus)
    events: list[GameOverEvent] = []
    event_bus.subscribe(GameOverEvent, events.append)

    engine.request_move(source, target)
    engine.wait(100)
    engine.wait(100)

    assert engine.game_over
    assert events == [GameOverEvent(winner=PieceColor.WHITE)]
