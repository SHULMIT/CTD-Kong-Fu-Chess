"""Server tests for authoritative profiles and completed-game ratings."""

import asyncio
import json

from app.game_engine_factory import GameEngineFactory
from authentication.authentication_service import AuthenticationService
from authentication.sqlite_user_repository import SQLiteUserRepository
from model.piece import PieceColor
from network.server.game_server import GameServer
from rating.elo_rating_service import EloRatingService
from rating.persistent_rating_service import PersistentRatingService
from tests.network.test_game_server import FakeConnection
from tests.unit.test_authentication_service import FastTestHasher


def test_profiles_and_updated_ratings_are_broadcast_to_both_clients(
    tmp_path,
) -> None:
    async def scenario() -> None:
        repository = SQLiteUserRepository(tmp_path / "users.db")
        authentication = AuthenticationService(
            repository,
            password_hasher=FastTestHasher(),
        )
        authentication.initialize()
        authentication.register("WhitePlayer", "password123")
        authentication.register("BlackPlayer", "password123")
        server = GameServer(
            GameEngineFactory.create(),
            authentication_service=authentication,
            rating_service=PersistentRatingService(
                repository,
                EloRatingService(),
            ),
        )
        white = FakeConnection()
        black = FakeConnection()

        await server.handle_message(
            white,
            json.dumps(
                {
                    "type": "login",
                    "username": "WhitePlayer",
                    "password": "password123",
                }
            ),
        )
        await server.handle_message(
            black,
            json.dumps(
                {
                    "type": "login",
                    "username": "BlackPlayer",
                    "password": "password123",
                }
            ),
        )
        await server.handle_message(
            white, json.dumps({"type": "start_matchmaking"})
        )
        await server.handle_message(
            black, json.dumps({"type": "start_matchmaking"})
        )

        white_messages = [await white.receive() for _ in range(6)]
        black_messages = [await black.receive() for _ in range(5)]
        profiles = next(
            message for message in white_messages
            if message["type"] == "match_found"
        )
        assert profiles["players"] == [
            {"username": "WhitePlayer", "color": "white", "rating": 1200},
            {"username": "BlackPlayer", "color": "black", "rating": 1200},
        ]
        assert next(
            message for message in black_messages
            if message["type"] == "match_found"
        ) == profiles

        await server._finalize_ratings(PieceColor.WHITE)

        white_update = await white.receive()
        black_update = await black.receive()
        assert white_update == black_update
        assert white_update == {
            "type": "rating_updated",
            "players": [
                {
                    "username": "WhitePlayer",
                    "color": "white",
                    "rating": 1216,
                    "rating_change": 16,
                },
                {
                    "username": "BlackPlayer",
                    "color": "black",
                    "rating": 1184,
                    "rating_change": -16,
                },
            ],
        }

    asyncio.run(scenario())


def test_unfinished_game_does_not_change_ratings(tmp_path) -> None:
    repository = SQLiteUserRepository(tmp_path / "users.db")
    authentication = AuthenticationService(
        repository,
        password_hasher=FastTestHasher(),
    )
    authentication.initialize()
    white = authentication.register("WhitePlayer", "password123")
    black = authentication.register("BlackPlayer", "password123")
    GameServer(
        GameEngineFactory.create(),
        authentication_service=authentication,
        rating_service=PersistentRatingService(repository, EloRatingService()),
    )

    assert authentication.login("WhitePlayer", "password123") == white
    assert authentication.login("BlackPlayer", "password123") == black
