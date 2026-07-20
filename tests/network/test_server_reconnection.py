"""Server tests for temporary disconnect and session resume routing."""

import asyncio
import json

from app.game_engine_factory import GameEngineFactory
from authentication.authentication_service import AuthenticationService
from authentication.sqlite_user_repository import SQLiteUserRepository
from network.game_server import GameServer
from network.reconnect_session_service import ReconnectSessionService
from tests.network.test_game_server import FakeConnection
from tests.unit.test_authentication_service import FastTestHasher


def test_disconnect_pauses_commands_and_resume_restores_snapshot(tmp_path) -> None:
    async def scenario() -> None:
        server, white, black, white_token, _ = await _matched_server(tmp_path)
        await server._handle_disconnect(white)
        disconnected = await black.receive()
        assert disconnected["type"] == "opponent_disconnected"
        assert disconnected["username"] == "WhitePlayer"

        await server.handle_message(
            black,
            json.dumps({
                "type": "move",
                "source": {"row": 1, "column": 0},
                "target": {"row": 2, "column": 0},
            }),
        )
        assert await black.receive() == {
            "type": "game_paused",
            "reason": "opponent_disconnected",
        }

        replacement = FakeConnection()
        await server.handle_message(
            replacement,
            json.dumps({"type": "resume_session", "token": white_token}),
        )
        resumed_messages = [await replacement.receive() for _ in range(4)]
        assert resumed_messages[0] == {
            "type": "session_resumed",
            "game_id": disconnected["game_id"],
            "color": "white",
        }
        assert resumed_messages[1]["type"] == "session_resume_token"
        assert resumed_messages[2]["type"] == "game_snapshot"
        assert resumed_messages[3]["type"] == "player_profiles"
        assert (await black.receive())["type"] == "opponent_reconnected"

        invalid = FakeConnection()
        await server.handle_message(
            invalid,
            json.dumps({"type": "resume_session", "token": white_token}),
        )
        assert (await invalid.receive())["type"] == "session_resume_rejected"

    asyncio.run(scenario())


def test_timeout_forfeit_is_once_and_uses_rating_service(tmp_path) -> None:
    async def scenario() -> None:
        server, white, black, _, _ = await _matched_server(
            tmp_path, timeout=0.01, with_ratings=True
        )
        await server._handle_disconnect(white)
        await black.receive()
        await asyncio.sleep(0.04)

        messages = []
        while not black.outgoing.empty():
            messages.append(await black.receive())
        assert sum(message["type"] == "disconnect_forfeit" for message in messages) == 1
        assert sum(message["type"] == "rating_updated" for message in messages) == 1
        authentication = server._authentication_service
        assert authentication.current_user("BlackPlayer").rating == 1216
        assert authentication.current_user("WhitePlayer").rating == 1184
        assert server._reconnect.participant_for_connection(black) is None

    asyncio.run(scenario())


async def _matched_server(tmp_path, timeout=20, with_ratings=False):
    from rating.elo_rating_service import EloRatingService
    from rating.persistent_rating_service import PersistentRatingService

    repository = SQLiteUserRepository(tmp_path / "users.db")
    authentication = AuthenticationService(repository, FastTestHasher())
    authentication.initialize()
    authentication.register("WhitePlayer", "password123")
    authentication.register("BlackPlayer", "password123")
    rating_service = (
        PersistentRatingService(repository, EloRatingService()) if with_ratings else None
    )
    server = GameServer(
        GameEngineFactory.create(),
        authentication_service=authentication,
        rating_service=rating_service,
        reconnect_service=ReconnectSessionService(timeout),
    )
    white, black = FakeConnection(), FakeConnection()
    for connection, username in ((white, "WhitePlayer"), (black, "BlackPlayer")):
        await server.handle_message(
            connection,
            json.dumps({"type": "login", "username": username, "password": "password123"}),
        )
        await connection.receive()
    await server.handle_message(white, json.dumps({"type": "start_matchmaking"}))
    await white.receive()
    await server.handle_message(black, json.dumps({"type": "start_matchmaking"}))
    white_messages = [await white.receive() for _ in range(4)]
    black_messages = [await black.receive() for _ in range(4)]
    return server, white, black, white_messages[3]["token"], black_messages[3]["token"]
