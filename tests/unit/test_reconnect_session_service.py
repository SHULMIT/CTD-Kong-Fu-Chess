"""Deterministic tests for resumable game participant sessions."""

from authentication.user import User
from model.piece import PieceColor
from network.reconnect_session_service import (
    ParticipantConnectionState,
    ReconnectSessionService,
)


def test_disconnect_resume_preserves_identity_color_and_rotates_token() -> None:
    now = [100.0]
    service = ReconnectSessionService(20, clock=lambda: now[0])
    old, opponent, replacement = object(), object(), object()
    player = User(1, "Dan", 1200)
    tokens = service.create_game(
        "game-1",
        (
            (old, player, PieceColor.WHITE),
            (opponent, User(2, "Noa", 1210), PieceColor.BLACK),
        ),
    )

    notice = service.disconnect(old)
    result = service.resume(replacement, tokens[old])

    assert notice is not None and notice.deadline == 120.0
    assert result is not None
    assert result.game_id == "game-1"
    assert result.user == player
    assert result.color is PieceColor.WHITE
    assert result.token != tokens[old]
    assert service.resume(object(), tokens[old]) is None
    assert service.participant_for_connection(replacement).state is ParticipantConnectionState.CONNECTED
    assert service.disconnect(old) is None


def test_expiry_is_idempotent_and_both_absent_has_no_winner() -> None:
    now = [10.0]
    service = ReconnectSessionService(2, clock=lambda: now[0])
    first, second = object(), object()
    service.create_game(
        "game-2",
        (
            (first, User(1, "Dan", 1200), PieceColor.WHITE),
            (second, User(2, "Noa", 1200), PieceColor.BLACK),
        ),
    )
    first_notice = service.disconnect(first)
    service.disconnect(second)
    now[0] = 12.0

    result = service.expire(1, first_notice.deadline)

    assert result is not None
    assert result.winner is None
    assert service.expire(1, first_notice.deadline) is None


def test_connected_opponent_wins_only_after_authoritative_deadline() -> None:
    now = [1.0]
    service = ReconnectSessionService(5, clock=lambda: now[0])
    first, second = object(), object()
    service.create_game(
        "game-3",
        (
            (first, User(1, "Dan", 1200), PieceColor.WHITE),
            (second, User(2, "Noa", 1200), PieceColor.BLACK),
        ),
    )
    notice = service.disconnect(first)
    assert service.expire(1, notice.deadline) is None
    now[0] = 6.0

    result = service.expire(1, notice.deadline)

    assert result is not None
    assert result.winner.username == "Noa"
    assert result.loser.username == "Dan"
    assert result.winner_color is PieceColor.BLACK
    assert service.resume(object(), "invalid") is None
