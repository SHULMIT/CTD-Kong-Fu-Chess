"""Focused tests for spectator membership and active-game metadata."""

from authentication.user import User
from spectators.spectator_service import SpectatableGame, SpectatorService


def test_multiple_spectators_join_leave_and_game_cleanup() -> None:
    service = SpectatorService()
    game = SpectatableGame(
        "game-1", User(1, "Dan", 1216), User(2, "Noa", 1199)
    )
    first, second = object(), object()
    service.register_game(game)

    assert service.list_games() == (game,)
    assert service.join("game-1", first)
    assert service.join("game-1", second)
    assert not service.join("missing", object())
    assert not service.join("game-1", first)
    assert set(service.spectators_for("game-1")) == {first, second}
    assert service.leave(first) == "game-1"
    assert service.close_game("game-1") == (second,)
    assert service.list_games() == ()
    assert not service.is_spectator(second)
