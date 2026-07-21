"""Important multiplayer actions emit one structured server event."""

import asyncio
import json
import logging

from app.game_engine_factory import GameEngineFactory
from authentication.authentication_service import AuthenticationService
from authentication.sqlite_user_repository import SQLiteUserRepository
from network.server.game_server import GameServer
from tests.network.test_game_server import FakeConnection
from tests.unit.test_authentication_service import FastTestHasher


def test_authentication_matchmaking_and_game_start_are_logged(tmp_path, caplog) -> None:
    async def scenario() -> None:
        authentication = AuthenticationService(
            SQLiteUserRepository(tmp_path / "users.db"), FastTestHasher()
        )
        authentication.initialize()
        logger = logging.getLogger("test.multiplayer.logging")
        server = GameServer(
            GameEngineFactory.create(),
            authentication_service=authentication,
            logger=logger,
        )
        first, second = FakeConnection(), FakeConnection()
        for connection, username in ((first, "PlayerOne"), (second, "PlayerTwo")):
            await server.handle_message(
                connection,
                json.dumps({
                    "type": "register", "username": username, "password": "password123"
                }),
            )
            await connection.receive()
            await server.handle_message(
                connection,
                json.dumps({
                    "type": "login", "username": username, "password": "password123"
                }),
            )
            await connection.receive()
        await server.handle_message(first, json.dumps({"type": "start_matchmaking"}))
        await first.receive()
        await server.handle_message(second, json.dumps({"type": "start_matchmaking"}))

    with caplog.at_level(logging.INFO, logger="test.multiplayer.logging"):
        asyncio.run(scenario())

    events = [getattr(record, "event_type", None) for record in caplog.records]
    assert events.count("registration_succeeded") == 2
    assert events.count("login_succeeded") == 2
    assert events.count("matchmaking_joined") == 1
    assert events.count("match_created") == 1
    assert events.count("game_started") == 1
    combined = "\n".join(record.getMessage() for record in caplog.records)
    assert "password123" not in combined
