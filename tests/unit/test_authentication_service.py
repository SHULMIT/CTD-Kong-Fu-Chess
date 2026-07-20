"""Tests for registration, login, hashing, and SQLite persistence."""

import hashlib
import sqlite3

import pytest

from authentication.authentication_service import AuthenticationService
from authentication.errors import InvalidCredentialsError, UsernameTakenError
from authentication.password_hasher import ScryptPasswordHasher
from authentication.sqlite_user_repository import SQLiteUserRepository


class FastTestHasher:
    def hash(self, password: str) -> str:
        return "test$" + hashlib.sha256(password.encode()).hexdigest()

    def verify(self, password: str, encoded_hash: str) -> bool:
        return self.hash(password) == encoded_hash


def _service(database_path) -> AuthenticationService:
    service = AuthenticationService(
        SQLiteUserRepository(database_path),
        password_hasher=FastTestHasher(),
    )
    service.initialize()
    return service


def test_registration_initializes_rating_and_login_returns_user(tmp_path) -> None:
    service = _service(tmp_path / "users.db")

    registered = service.register("Player_1", "password123")
    logged_in = service.login("Player_1", "password123")

    assert registered.rating == 1200
    assert logged_in == registered


def test_duplicate_username_is_rejected(tmp_path) -> None:
    service = _service(tmp_path / "users.db")
    service.register("Player_1", "password123")

    with pytest.raises(UsernameTakenError):
        service.register("Player_1", "different123")


def test_wrong_password_is_rejected(tmp_path) -> None:
    service = _service(tmp_path / "users.db")
    service.register("Player_1", "password123")

    with pytest.raises(InvalidCredentialsError):
        service.login("Player_1", "wrong-password")


def test_account_persists_across_service_restart(tmp_path) -> None:
    database_path = tmp_path / "users.db"
    first_service = _service(database_path)
    registered = first_service.register("Persistent", "password123")

    restarted_service = _service(database_path)

    assert restarted_service.login("Persistent", "password123") == registered


def test_database_never_stores_plaintext_password(tmp_path) -> None:
    database_path = tmp_path / "users.db"
    service = _service(database_path)
    service.register("Player_1", "password123")

    with sqlite3.connect(database_path) as connection:
        stored_hash = connection.execute(
            "SELECT password_hash FROM users WHERE username = ?",
            ("Player_1",),
        ).fetchone()[0]

    assert stored_hash != "password123"
    assert "password123" not in stored_hash


def test_scrypt_hasher_uses_unique_salts_and_verifies_password() -> None:
    hasher = ScryptPasswordHasher()

    first_hash = hasher.hash("password123")
    second_hash = hasher.hash("password123")

    assert first_hash != second_hash
    assert hasher.verify("password123", first_hash)
    assert not hasher.verify("wrong-password", first_hash)
