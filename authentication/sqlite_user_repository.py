"""SQLite-backed server-side user account persistence."""

from pathlib import Path
import sqlite3

from authentication.errors import UsernameTakenError
from authentication.user import User
from authentication.user_repository import StoredUser


class SQLiteUserRepository:
    """Creates and queries a migration-safe SQLite users table."""

    def __init__(self, database_path: str | Path) -> None:
        self._database_path = Path(database_path)

    def initialize(self) -> None:
        """Create the database and users table if they don't already exist."""
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    rating INTEGER NOT NULL DEFAULT 1200,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS game_results (
                    game_id TEXT PRIMARY KEY,
                    winner_user_id INTEGER NOT NULL,
                    loser_user_id INTEGER NOT NULL,
                    winner_rating INTEGER NOT NULL,
                    loser_rating INTEGER NOT NULL,
                    completed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (winner_user_id) REFERENCES users(id),
                    FOREIGN KEY (loser_user_id) REFERENCES users(id)
                )
                """
            )

    def create(self, username: str, password_hash: str, rating: int) -> User:
        """Persist and return a new account."""
        try:
            with self._connect() as connection:
                cursor = connection.execute(
                    """
                    INSERT INTO users (username, password_hash, rating)
                    VALUES (?, ?, ?)
                    """,
                    (username, password_hash, rating),
                )
                user_id = int(cursor.lastrowid)
        except sqlite3.IntegrityError as error:
            raise UsernameTakenError() from error
        return User(id=user_id, username=username, rating=rating)

    def find_by_username(self, username: str) -> StoredUser | None:
        """Return a stored account by its unique username."""
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT id, username, password_hash, rating
                FROM users
                WHERE username = ?
                """,
                (username,),
            ).fetchone()
        if row is None:
            return None
        return StoredUser(
            user=User(id=row[0], username=row[1], rating=row[3]),
            password_hash=row[2],
        )

    def apply_rating_update(
        self,
        game_id: str,
        winner_id: int,
        loser_id: int,
        winner_rating: int,
        loser_rating: int,
    ) -> bool:
        """Atomically record a unique result and update both ratings."""
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            winner_update = connection.execute(
                "UPDATE users SET rating = ? WHERE id = ?",
                (winner_rating, winner_id),
            )
            loser_update = connection.execute(
                "UPDATE users SET rating = ? WHERE id = ?",
                (loser_rating, loser_id),
            )
            if winner_update.rowcount != 1 or loser_update.rowcount != 1:
                raise RuntimeError("Both rating owners must exist.")
            connection.execute(
                """
                INSERT INTO game_results (
                    game_id,
                    winner_user_id,
                    loser_user_id,
                    winner_rating,
                    loser_rating
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    game_id,
                    winner_id,
                    loser_id,
                    winner_rating,
                    loser_rating,
                ),
            )
            connection.commit()
            return True
        except sqlite3.IntegrityError:
            connection.rollback()
            if self._game_result_exists(connection, game_id):
                return False
            raise
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def _game_result_exists(
        connection: sqlite3.Connection,
        game_id: str,
    ) -> bool:
        row = connection.execute(
            "SELECT 1 FROM game_results WHERE game_id = ?",
            (game_id,),
        ).fetchone()
        return row is not None

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._database_path)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection
