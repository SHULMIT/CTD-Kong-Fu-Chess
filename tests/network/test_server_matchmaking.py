"""Server boundary tests for authoritative matchmaking."""

import asyncio
import json

from app.game_engine_factory import GameEngineFactory
from authentication.authentication_service import AuthenticationService
from authentication.sqlite_user_repository import SQLiteUserRepository
from network.server.game_server import GameServer
from tests.network.test_game_server import FakeConnection
from tests.unit.test_authentication_service import FastTestHasher


def test_two_authenticated_compatible_players_create_exactly_one_match(tmp_path) -> None:
    async def scenario() -> None:
        repository = SQLiteUserRepository(tmp_path / "users.db")
        authentication = AuthenticationService(repository, FastTestHasher())
        authentication.initialize()
        authentication.register("PlayerOne", "password123")
        authentication.register("PlayerTwo", "password123")
        server = GameServer(
            GameEngineFactory.create(), authentication_service=authentication
        )
        first, second = FakeConnection(), FakeConnection()
        await _login(server, first, "PlayerOne")
        await _login(server, second, "PlayerTwo")

        await server.handle_message(first, json.dumps({"type": "start_matchmaking"}))
        assert await first.receive() == {"type": "matchmaking_queued", "rating": 1200}
        await server.handle_message(second, json.dumps({"type": "start_matchmaking"}))

        first_messages = [await first.receive() for _ in range(3)]
        second_messages = [await second.receive() for _ in range(3)]
        first_match = first_messages[0]
        second_match = second_messages[0]
        assert first_match == second_match
        assert first_match["type"] == "match_found"
        assert len(first_match["players"]) == 2
        assert first_match["game_id"]
        assert {message["type"] for message in first_messages[1:]} == {
            "connection_accepted", "game_snapshot"
        }

    asyncio.run(scenario())


def test_cancel_disconnect_and_unauthenticated_queue_are_safe(tmp_path) -> None:
    async def scenario() -> None:
        repository = SQLiteUserRepository(tmp_path / "users.db")
        authentication = AuthenticationService(repository, FastTestHasher())
        authentication.initialize()
        authentication.register("PlayerOne", "password123")
        server = GameServer(
            GameEngineFactory.create(), authentication_service=authentication
        )
        unauthenticated, player = FakeConnection(), FakeConnection()
        await server.handle_message(
            unauthenticated, json.dumps({"type": "start_matchmaking"})
        )
        assert (await unauthenticated.receive())["reason"] == "authentication_required"
        await _login(server, player, "PlayerOne")
        await server.handle_message(player, json.dumps({"type": "start_matchmaking"}))
        await player.receive()
        await server.handle_message(player, json.dumps({"type": "cancel_matchmaking"}))
        assert await player.receive() == {"type": "matchmaking_canceled"}
        server._matchmaking.disconnect(player)
        assert server._matchmaking.queued_entries == ()

    asyncio.run(scenario())


def test_matchmaking_refreshes_the_latest_persistent_rating(tmp_path) -> None:
    async def scenario() -> None:
        repository = SQLiteUserRepository(tmp_path / "users.db")
        authentication = AuthenticationService(repository, FastTestHasher())
        authentication.initialize()
        player = authentication.register("PlayerOne", "password123")
        other = authentication.register("OtherUser", "password123")
        server = GameServer(
            GameEngineFactory.create(), authentication_service=authentication
        )
        connection = FakeConnection()
        await _login(server, connection, "PlayerOne")
        assert repository.apply_rating_update(
            "previous-game", player.id, other.id, 1288, 1112
        )

        await server.handle_message(
            connection, json.dumps({"type": "start_matchmaking"})
        )

        assert await connection.receive() == {
            "type": "matchmaking_queued",
            "rating": 1288,
        }

    asyncio.run(scenario())


async def _login(server: GameServer, connection: FakeConnection, username: str) -> None:
    await server.handle_message(
        connection,
        json.dumps({"type": "login", "username": username, "password": "password123"}),
    )
    assert (await connection.receive())["type"] == "login_success"
