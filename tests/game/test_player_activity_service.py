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


def _record_moves(
    service: PlayerActivityService,
    player: PieceColor,
    count: int,
) -> None:
    for timestamp in range(count):
        service.record_move(
            player=player,
            piece_type=PieceType.PAWN,
            source=Position(6, 0),
            target=Position(5, 0),
            timestamp_milliseconds=timestamp,
        )


def test_records_actions_at_their_simulation_time():
    service = PlayerActivityService()

    service.record_move(
        player=PieceColor.WHITE,
        piece_type=PieceType.PAWN,
        source=Position(6, 0),
        target=Position(5, 0),
        timestamp_milliseconds=3_250,
    )

    actions = service.get_actions(PieceColor.WHITE)
    assert len(actions) == 1
    assert actions[0].timestamp_milliseconds == 3_250
    assert actions[0].description == "Pawn A2 -> A3"


def test_awards_standard_points_for_captured_pieces():
    service = PlayerActivityService()

    service.record_capture(PieceColor.BLACK, PieceType.QUEEN)
    service.record_capture(PieceColor.BLACK, PieceType.PAWN)

    assert service.get_score(PieceColor.BLACK) == 10
    assert service.get_score(PieceColor.WHITE) == 0


def test_retains_fewer_than_eight_actions_for_a_player():
    service = PlayerActivityService()

    _record_moves(service, PieceColor.WHITE, 3)

    assert len(service.get_actions(PieceColor.WHITE)) == 3


def test_retains_exactly_eight_actions_for_a_player():
    service = PlayerActivityService()

    _record_moves(service, PieceColor.WHITE, service.MAX_PLAYER_ACTIONS)

    assert [
        action.timestamp_milliseconds
        for action in service.get_actions(PieceColor.WHITE)
    ] == list(range(service.MAX_PLAYER_ACTIONS))


def test_ninth_action_removes_the_oldest_action_for_that_player():
    service = PlayerActivityService()

    _record_moves(service, PieceColor.WHITE, service.MAX_PLAYER_ACTIONS + 1)

    assert [
        action.timestamp_milliseconds
        for action in service.get_actions(PieceColor.WHITE)
    ] == list(range(1, service.MAX_PLAYER_ACTIONS + 1))


def test_white_and_black_histories_have_independent_limits():
    service = PlayerActivityService()

    _record_moves(service, PieceColor.WHITE, service.MAX_PLAYER_ACTIONS + 1)
    _record_moves(service, PieceColor.BLACK, 2)

    assert len(service.get_actions(PieceColor.WHITE)) == service.MAX_PLAYER_ACTIONS
    assert len(service.get_actions(PieceColor.BLACK)) == 2
    assert service.get_actions(PieceColor.BLACK)[0].timestamp_milliseconds == 0


def test_returned_history_cannot_mutate_the_service_collection():
    service = PlayerActivityService()
    _record_moves(service, PieceColor.WHITE, 1)

    actions = service.get_actions(PieceColor.WHITE)

    with pytest.raises(AttributeError):
        actions.append(actions[0])
    assert len(service.get_actions(PieceColor.WHITE)) == 1


def test_game_records_move_time_and_awards_capture_score():
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
    assert action.timestamp_milliseconds == 0
    assert action.description == "Rook A8 -> B8"
