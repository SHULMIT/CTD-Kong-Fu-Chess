"""Unit tests for local client color ownership."""

from model.piece import PieceColor
from network.server.matches.session_manager import SessionManager


def test_first_client_receives_white() -> None:
    sessions = SessionManager()

    assert sessions.connect(object()) is PieceColor.WHITE


def test_second_client_receives_black_without_duplicate_color() -> None:
    sessions = SessionManager()
    first = object()
    second = object()

    first_color = sessions.connect(first)
    second_color = sessions.connect(second)

    assert first_color is PieceColor.WHITE
    assert second_color is PieceColor.BLACK
    assert first_color is not second_color


def test_third_client_is_rejected() -> None:
    sessions = SessionManager()
    sessions.connect(object())
    sessions.connect(object())

    assert sessions.connect(object()) is None


def test_disconnect_releases_color() -> None:
    sessions = SessionManager()
    first = object()
    sessions.connect(first)
    sessions.connect(object())

    sessions.disconnect(first)

    assert sessions.connect(object()) is PieceColor.WHITE


def test_ownership_checks_match_assigned_color() -> None:
    sessions = SessionManager()
    client = object()
    sessions.connect(client)

    assert sessions.can_control(client, PieceColor.WHITE)
    assert not sessions.can_control(client, PieceColor.BLACK)
    assert not sessions.can_control(object(), PieceColor.WHITE)
