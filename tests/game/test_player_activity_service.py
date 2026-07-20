from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

from game.player_activity_service import PlayerActivityService
from game.game_engine import GameEngine
from model.board import Board
from model.piece import PieceColor, PieceType
from model.piece import Piece
from model.position import Position
from realtime.duration_calculator import DurationCalculator
from realtime.real_time_arbiter import RealTimeArbiter
from rules.rule_engine import RuleEngine
import pytest


def _record_moves(service: PlayerActivityService, player: PieceColor, count: int) -> None:
    for _ in range(count):
        service.record_move(
            player=player,
            piece_type=PieceType.PAWN,
            source=Position(6, 0),
            target=Position(5, 0),
        )


def test_default_clock_records_timezone_aware_utc_time():
    service = PlayerActivityService()

    _record_moves(service, PieceColor.WHITE, 1)

    occurred_at = service.get_actions(PieceColor.WHITE)[0].occurred_at
    assert occurred_at.tzinfo is not None
    assert occurred_at.utcoffset() == timedelta(0)


def test_injected_clock_is_used_exactly():
    current_time = datetime(2026, 7, 19, 14, 5, 9, 321_000, tzinfo=timezone.utc)
    clock = Mock(return_value=current_time)
    service = PlayerActivityService(clock=clock)

    service.record_move(
        player=PieceColor.WHITE,
        piece_type=PieceType.PAWN,
        source=Position(6, 0),
        target=Position(5, 0),
    )

    actions = service.get_actions(PieceColor.WHITE)
    clock.assert_called_once_with()
    assert len(actions) == 1
    assert actions[0].occurred_at == current_time
    assert actions[0].description == "Pawn A2 -> A3"


def test_actions_remain_in_recording_order():
    service = PlayerActivityService()

    service.record_move(
        PieceColor.WHITE,
        PieceType.PAWN,
        Position(6, 0),
        Position(5, 0),
    )
    service.record_jump(PieceColor.WHITE, PieceType.PAWN, Position(5, 0))

    assert [
        action.description for action in service.get_actions(PieceColor.WHITE)
    ] == ["Pawn A2 -> A3", "Pawn jumps at A3"]


def test_awards_standard_points_for_captured_pieces():
    service = PlayerActivityService()

    service.record_capture(PieceColor.BLACK, PieceType.QUEEN)
    service.record_capture(PieceColor.BLACK, PieceType.PAWN)

    assert service.get_score(PieceColor.BLACK) == 10
    assert service.get_score(PieceColor.WHITE) == 0


def test_retains_every_action_for_a_player():
    service = PlayerActivityService()

    _record_moves(service, PieceColor.WHITE, 12)

    assert len(service.get_actions(PieceColor.WHITE)) == 12


def test_white_and_black_histories_are_independent():
    service = PlayerActivityService()

    _record_moves(service, PieceColor.WHITE, 9)
    _record_moves(service, PieceColor.BLACK, 2)

    assert len(service.get_actions(PieceColor.WHITE)) == 9
    assert len(service.get_actions(PieceColor.BLACK)) == 2


def test_returned_history_cannot_mutate_the_service_collection():
    service = PlayerActivityService()
    _record_moves(service, PieceColor.WHITE, 1)

    actions = service.get_actions(PieceColor.WHITE)

    with pytest.raises(AttributeError):
        actions.append(actions[0])
    assert len(service.get_actions(PieceColor.WHITE)) == 1


def test_game_records_move_and_awards_capture_score():
    rook = Piece(1, PieceType.ROOK, PieceColor.WHITE, Position(0, 0))
    queen = Piece(2, PieceType.QUEEN, PieceColor.BLACK, Position(0, 1))
    board = Board([[rook, queen]])
    arbiter = RealTimeArbiter(board)
    engine = GameEngine(
        board=board,
        rule_engine=RuleEngine(),
        arbiter=arbiter,
        duration_calculator=DurationCalculator(),
    )

    result = engine.request_move(Position(0, 0), Position(0, 1))
    engine.wait(500)

    assert result.is_accepted
    assert engine.player_activity.get_score(PieceColor.WHITE) == 9
    action = engine.player_activity.get_actions(PieceColor.WHITE)[0]
    assert isinstance(action.occurred_at, datetime)
    assert action.description == "Rook A8 -> B8"
