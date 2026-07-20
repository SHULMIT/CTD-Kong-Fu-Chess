"""Tests for atomic, idempotent SQLite rating persistence."""

import sqlite3

import pytest

from authentication.authentication_service import AuthenticationService
from authentication.sqlite_user_repository import SQLiteUserRepository
from rating.elo_rating_service import EloRatingService
from rating.persistent_rating_service import PersistentRatingService
from tests.unit.test_authentication_service import FastTestHasher


def _services(database_path):
    repository = SQLiteUserRepository(database_path)
    authentication = AuthenticationService(
        repository,
        password_hasher=FastTestHasher(),
    )
    authentication.initialize()
    ratings = PersistentRatingService(repository, EloRatingService())
    return authentication, repository, ratings


def test_winner_and_loser_ratings_persist_across_restart(tmp_path) -> None:
    database_path = tmp_path / "users.db"
    authentication, _, ratings = _services(database_path)
    winner = authentication.register("Winner_1", "password123")
    loser = authentication.register("Loser_1", "password123")

    update = ratings.record_result("game-1", winner, loser)

    assert update is not None
    assert update.winner.rating == 1216
    assert update.loser.rating == 1184
    restarted, _, _ = _services(database_path)
    assert restarted.login("Winner_1", "password123").rating == 1216
    assert restarted.login("Loser_1", "password123").rating == 1184


def test_duplicate_game_result_does_not_update_twice(tmp_path) -> None:
    authentication, _, ratings = _services(tmp_path / "users.db")
    winner = authentication.register("Winner_1", "password123")
    loser = authentication.register("Loser_1", "password123")

    first = ratings.record_result("same-game", winner, loser)
    duplicate = ratings.record_result("same-game", winner, loser)

    assert first is not None
    assert duplicate is None
    assert authentication.login("Winner_1", "password123").rating == 1216
    assert authentication.login("Loser_1", "password123").rating == 1184


def test_failed_second_user_update_rolls_back_entire_transaction(tmp_path) -> None:
    database_path = tmp_path / "users.db"
    authentication, repository, _ = _services(database_path)
    winner = authentication.register("Winner_1", "password123")

    with pytest.raises(RuntimeError):
        repository.apply_rating_update(
            game_id="atomic-game",
            winner_id=winner.id,
            loser_id=999999,
            winner_rating=1216,
            loser_rating=1184,
        )

    assert authentication.login("Winner_1", "password123").rating == 1200
    with sqlite3.connect(database_path) as connection:
        result_count = connection.execute(
            "SELECT COUNT(*) FROM game_results WHERE game_id = ?",
            ("atomic-game",),
        ).fetchone()[0]
    assert result_count == 0
