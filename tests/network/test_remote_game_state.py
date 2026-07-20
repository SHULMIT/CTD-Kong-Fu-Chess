"""Tests for UI state driven only by authoritative snapshots."""

from datetime import datetime, timedelta, timezone

from model.piece import PieceColor, PieceState, PieceType
from model.position import Position
from network.remote_game_state import RemoteGameState


class FakeNetworkClient:
    def __init__(self, messages: list[dict]) -> None:
        self._messages = messages

    def poll_messages(self) -> tuple[dict, ...]:
        messages = tuple(self._messages)
        self._messages.clear()
        return messages


def _snapshot_message() -> dict:
    return {
        "type": "game_snapshot",
        "state": {
            "board": {
                "width": 2,
                "height": 1,
                "pieces": [
                    {
                        "id": 7,
                        "type": "rook",
                        "color": "white",
                        "state": "moving",
                        "position": {"row": 0, "column": 0},
                    }
                ],
            },
            "motions": [
                {
                    "piece_id": 7,
                    "source": {"row": 0, "column": 0},
                    "target": {"row": 0, "column": 1},
                    "current_position": {"row": 0, "column": 0},
                    "duration": 1000,
                    "elapsed_time": 250,
                }
            ],
            "scores": {"white": 5, "black": 3},
            "game_over": True,
            "winner": "white",
        },
    }


def test_snapshot_is_the_authoritative_rendering_state() -> None:
    client = FakeNetworkClient([_snapshot_message()])
    state = RemoteGameState(client)

    state.wait(999999)

    piece = state.get_piece(Position(0, 0))
    assert piece is not None
    assert piece.id == 7
    assert piece.type is PieceType.ROOK
    assert piece.color is PieceColor.WHITE
    assert piece.state is PieceState.MOVING
    assert state.board.width == 2
    assert state.game_over
    assert state.get_winner() is PieceColor.WHITE
    assert state.player_activity.get_score(PieceColor.WHITE) == 5
    assert state.player_activity.get_score(PieceColor.BLACK) == 3
    motion = state.get_motions()[0]
    assert motion.piece is piece
    assert motion.elapsed_time == 250
    assert motion.target == Position(0, 1)


def test_network_responses_and_events_are_consumed_on_calling_thread() -> None:
    messages = [
        {"type": "command_accepted", "command": "move"},
        {"type": "game_event", "event": {"type": "move_started"}},
        {"type": "command_rejected", "reason": "not_your_piece"},
        {"type": "server_error"},
    ]
    state = RemoteGameState(FakeNetworkClient(messages))

    state.wait(0)

    assert state.last_event == {
        "type": "game_event",
        "event": {"type": "move_started"},
    }
    assert state.last_response == {"type": "server_error"}


def test_remote_state_never_predicts_legal_moves() -> None:
    state = RemoteGameState(FakeNetworkClient([_snapshot_message()]))
    state.wait(0)

    assert state.get_legal_moves(Position(0, 0)) == set()


def test_legal_move_markers_are_updated_and_cleared_by_snapshot() -> None:
    source = Position(0, 0)
    client = FakeNetworkClient(
        [
            _snapshot_message(),
            {
                "type": "legal_moves",
                "source": {"row": 0, "column": 0},
                "positions": [
                    {"row": 0, "column": 1},
                    {"row": 1, "column": 0},
                ],
            },
        ]
    )
    state = RemoteGameState(client)
    state.wait(0)

    assert state.get_legal_moves(source) == {
        Position(0, 1),
        Position(1, 0),
    }

    invalidating_snapshot = _snapshot_message()
    invalidating_snapshot["state"]["board"]["pieces"] = []
    state.apply_message(invalidating_snapshot)

    assert state.get_legal_moves(source) == set()


def test_game_events_populate_activity_without_duplicates() -> None:
    state = RemoteGameState(FakeNetworkClient([_snapshot_message()]))
    state.wait(0)
    move_event = {
        "type": "game_event",
        "event_id": 10,
        "event": {
            "type": "move_started",
            "piece_id": 7,
            "source": {"row": 0, "column": 0},
            "target": {"row": 0, "column": 1},
        },
    }
    jump_event = {
        "type": "game_event",
        "event_id": 11,
        "event": {
            "type": "jump_started",
            "piece_id": 7,
            "position": {"row": 0, "column": 0},
        },
    }
    score_event = {
        "type": "game_event",
        "event_id": 12,
        "event": {
            "type": "score_changed",
            "player": "white",
            "score": 9,
        },
    }
    game_over_event = {
        "type": "game_event",
        "event_id": 13,
        "event": {"type": "game_over", "winner": "white"},
    }

    for event in (move_event, move_event, jump_event, score_event, game_over_event):
        state.apply_message(event)
    state.apply_message(_snapshot_message())

    descriptions = [
        action.description
        for action in state.player_activity.get_actions(PieceColor.WHITE)
    ]
    assert descriptions == [
        "Rook A8 -> B8",
        "Rook jumps at A8",
        "Capture - score: 9",
        "Game over - White wins",
    ]


def test_both_profiles_and_rating_updates_are_authoritative() -> None:
    client = FakeNetworkClient([])
    client.assigned_color = PieceColor.WHITE
    state = RemoteGameState(client)
    profiles = {
        "type": "player_profiles",
        "players": [
            {"username": "Dan", "color": "white", "rating": 1200},
            {"username": "Noa", "color": "black", "rating": 1215},
        ],
    }

    state.apply_message(profiles)

    assert state.player_activity.get_profile(PieceColor.WHITE) == (
        "Dan", 1200, True
    )
    assert state.player_activity.get_profile(PieceColor.BLACK) == (
        "Noa", 1215, False
    )
    assert state.consume_match_started_message() == (
        "White: Dan (1200)\nBlack: Noa (1215)"
    )
    assert state.consume_match_started_message() is None

    state.apply_message(
        {
            "type": "rating_updated",
            "players": [
                {"username": "Dan", "color": "white", "rating": 1216},
                {"username": "Noa", "color": "black", "rating": 1199},
            ],
        }
    )

    assert state.player_activity.get_profile(PieceColor.WHITE) == (
        "Dan", 1216, True
    )
    assert state.player_activity.get_profile(PieceColor.BLACK) == (
        "Noa", 1199, False
    )


def test_disconnect_overlay_clears_after_opponent_resumes() -> None:
    state = RemoteGameState(FakeNetworkClient([]))
    state.apply_message(
        {
            "type": "opponent_disconnected",
            "username": "Noa",
            "deadline": (datetime.now(timezone.utc) + timedelta(seconds=20)).isoformat(),
        }
    )

    assert "Waiting for Noa" in state.disconnect_overlay_message()

    state.apply_message({"type": "opponent_reconnected", "username": "Noa"})
    assert state.disconnect_overlay_message() == "Opponent reconnected"
