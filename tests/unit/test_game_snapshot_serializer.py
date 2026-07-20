"""Unit tests for JSON-safe game snapshot serialization."""

import json
from types import SimpleNamespace
from unittest.mock import MagicMock

from config.constants import EMPTY_SQUARE
from events.event_bus import EventBus
from game.game_engine import GameEngine
from game.move_reason import MoveReason
from model.board import Board
from model.piece import Piece, PieceColor, PieceState, PieceType
from model.position import Position
from network.game_snapshot_serializer import GameSnapshotSerializer
from realtime.duration_calculator import DurationCalculator
from realtime.real_time_arbiter import RealTimeArbiter


def _create_game() -> tuple[GameEngine, Piece, Piece]:
    rook = Piece(
        1,
        PieceType.ROOK,
        PieceColor.WHITE,
        Position(0, 0),
    )
    king = Piece(
        2,
        PieceType.KING,
        PieceColor.BLACK,
        Position(1, 1),
    )
    board = Board(
        [
            [rook, EMPTY_SQUARE],
            [EMPTY_SQUARE, king],
        ]
    )
    rule_engine = MagicMock()
    rule_engine.validate_move.return_value = SimpleNamespace(
        is_valid=True,
        reason=MoveReason.OK,
    )
    duration_calculator = MagicMock(spec=DurationCalculator)
    duration_calculator.calculate.return_value = 1000
    engine = GameEngine(
        board=board,
        rule_engine=rule_engine,
        arbiter=RealTimeArbiter(board),
        duration_calculator=duration_calculator,
        event_bus=EventBus(),
    )
    return engine, rook, king


def test_snapshot_contains_representative_board_and_game_state() -> None:
    engine, _, _ = _create_game()

    snapshot = GameSnapshotSerializer().serialize(engine)

    assert snapshot["board"] == {
        "width": 2,
        "height": 2,
        "pieces": [
            {
                "id": 1,
                "type": "rook",
                "color": "white",
                "state": "idle",
                "position": {"row": 0, "column": 0},
            },
            {
                "id": 2,
                "type": "king",
                "color": "black",
                "state": "idle",
                "position": {"row": 1, "column": 1},
            },
        ],
    }
    assert snapshot["scores"] == {"white": 0, "black": 0}
    assert snapshot["game_over"] is False
    assert snapshot["winner"] == "black"


def test_positions_enums_and_active_motion_are_converted() -> None:
    engine, rook, _ = _create_game()
    engine.request_move(Position(0, 0), Position(0, 1))

    snapshot = GameSnapshotSerializer().serialize(engine)

    assert snapshot["motions"] == [
        {
            "piece_id": 1,
            "source": {"row": 0, "column": 0},
            "target": {"row": 0, "column": 1},
            "current_position": {"row": 0, "column": 0},
            "duration": 1000,
            "elapsed_time": 0,
        }
    ]
    assert snapshot["board"]["pieces"][0]["state"] == "moving"
    assert rook.state is PieceState.MOVING


def test_snapshot_contains_only_json_safe_values() -> None:
    engine, _, _ = _create_game()
    snapshot = GameSnapshotSerializer().serialize(engine)

    encoded = json.dumps(snapshot)

    assert json.loads(encoded) == snapshot


def test_serialization_does_not_mutate_game_state() -> None:
    engine, rook, king = _create_game()
    board = engine.get_board()
    state_before = (
        board.get_piece(Position(0, 0)),
        board.get_piece(Position(1, 1)),
        rook.position,
        rook.state,
        king.position,
        king.state,
        engine.get_motions(),
    )

    GameSnapshotSerializer().serialize(engine)

    state_after = (
        board.get_piece(Position(0, 0)),
        board.get_piece(Position(1, 1)),
        rook.position,
        rook.state,
        king.position,
        king.state,
        engine.get_motions(),
    )
    assert state_after == state_before


def test_repeated_serialization_is_deterministic() -> None:
    engine, _, _ = _create_game()
    serializer = GameSnapshotSerializer()

    first_snapshot = serializer.serialize(engine)
    second_snapshot = serializer.serialize(engine)

    assert second_snapshot == first_snapshot
    assert second_snapshot is not first_snapshot
