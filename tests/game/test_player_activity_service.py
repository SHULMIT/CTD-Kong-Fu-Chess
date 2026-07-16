from game.player_activity_service import PlayerActivityService
from game.game_engine import GameEngine
from model.board import Board
from model.piece import PieceColor, PieceType
from model.piece import Piece
from model.position import Position
from realtime.duration_calculator import DurationCalculator
from realtime.real_time_arbiter import RealTimeArbiter
from rules.rule_engine import RuleEngine


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
