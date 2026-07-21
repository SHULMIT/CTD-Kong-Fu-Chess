"""Server boundary tests for read-only active-game spectators."""

import asyncio
import json

from app.game_engine_factory import GameEngineFactory
from authentication.authentication_service import AuthenticationService
from authentication.sqlite_user_repository import SQLiteUserRepository
from network.server.game_server import GameServer
from tests.network.test_game_server import FakeConnection
from tests.unit.test_authentication_service import FastTestHasher


def test_listing_joining_updates_and_read_only_permissions(tmp_path) -> None:
    async def scenario() -> None:
        server, white, black, spectators, game_id = await _active_game(tmp_path, 2)
        first, second = spectators
        await server.handle_message(first, json.dumps({"type": "list_spectatable_games"}))
        listed = await first.receive()
        assert listed == {
            "type": "spectatable_games",
            "games": [{
                "game_id": game_id,
                "white": {"username": "WhitePlayer", "rating": 1200},
                "black": {"username": "BlackPlayer", "rating": 1200},
            }],
        }
        for spectator in spectators:
            await server.handle_message(
                spectator,
                json.dumps({"type": "spectate_game", "game_id": game_id}),
            )
            messages = [await spectator.receive() for _ in range(3)]
            assert [message["type"] for message in messages] == [
                "spectating_started", "game_snapshot", "player_profiles"
            ]
        assert len(server._spectators.spectators_for(game_id)) == 2

        await server.handle_message(
            first,
            json.dumps({
                "type": "move",
                "source": {"row": 6, "column": 0},
                "target": {"row": 5, "column": 0},
            }),
        )
        assert await first.receive() == {
            "type": "command_rejected", "reason": "spectator_read_only"
        }
        assert server.game_engine.get_motions() == ()

        await server.broadcast_snapshot()
        assert (await first.receive())["type"] == "game_snapshot"
        assert (await second.receive())["type"] == "game_snapshot"
        assert (await white.receive())["type"] == "game_snapshot"
        assert (await black.receive())["type"] == "game_snapshot"

    asyncio.run(scenario())


def test_stop_disconnect_and_game_end_cleanup_do_not_touch_players(tmp_path) -> None:
    async def scenario() -> None:
        server, white, black, spectators, game_id = await _active_game(tmp_path, 2)
        first, second = spectators
        for spectator in spectators:
            await server.handle_message(
                spectator,
                json.dumps({"type": "spectate_game", "game_id": game_id}),
            )
            for _ in range(3):
                await spectator.receive()

        await server.handle_message(first, json.dumps({"type": "stop_spectating"}))
        assert await first.receive() == {"type": "spectating_stopped"}
        await server._handle_disconnect(second)
        assert server._spectators.spectators_for(game_id) == ()
        assert len(server._sessions.clients) == 2
        assert not server._reconnect.is_paused()

        third = FakeConnection()
        await _login(server, third, "SpectatorOne")
        await server.handle_message(
            third, json.dumps({"type": "spectate_game", "game_id": game_id})
        )
        for _ in range(3):
            await third.receive()
        await server._close_spectator_views(game_id)
        assert await third.receive() == {
            "type": "spectating_stopped", "reason": "game_ended"
        }
        assert server._spectators.list_games() == ()
        assert len(server._sessions.clients) == 2

    asyncio.run(scenario())


async def _active_game(tmp_path, spectator_count):
    repository = SQLiteUserRepository(tmp_path / "users.db")
    authentication = AuthenticationService(repository, FastTestHasher())
    authentication.initialize()
    for username in ("WhitePlayer", "BlackPlayer", "SpectatorOne", "SpectatorTwo"):
        authentication.register(username, "password123")
    server = GameServer(GameEngineFactory.create(), authentication_service=authentication)
    white, black = FakeConnection(), FakeConnection()
    await _login(server, white, "WhitePlayer")
    await _login(server, black, "BlackPlayer")
    await server.handle_message(white, json.dumps({"type": "start_matchmaking"}))
    await white.receive()
    await server.handle_message(black, json.dumps({"type": "start_matchmaking"}))
    white_messages = [await white.receive() for _ in range(4)]
    for _ in range(4):
        await black.receive()
    game_id = white_messages[0]["game_id"]
    spectators = [FakeConnection() for _ in range(spectator_count)]
    for index, spectator in enumerate(spectators):
        await _login(server, spectator, f"Spectator{'One' if index == 0 else 'Two'}")
    return server, white, black, spectators, game_id


async def _login(server, connection, username):
    await server.handle_message(
        connection,
        json.dumps({"type": "login", "username": username, "password": "password123"}),
    )
    await connection.receive()
