"""WebSocket orchestration tests for authentication enforcement."""

import asyncio
import json

from app.game_engine_factory import GameEngineFactory
from authentication.authentication_service import AuthenticationService
from authentication.sqlite_user_repository import SQLiteUserRepository
from network.server.game_server import GameServer
from tests.network.test_game_server import FakeConnection
from tests.unit.test_authentication_service import FastTestHasher


def _authenticated_server(tmp_path) -> GameServer:
    service = AuthenticationService(
        SQLiteUserRepository(tmp_path / "users.db"),
        password_hasher=FastTestHasher(),
    )
    service.initialize()
    return GameServer(
        GameEngineFactory.create(),
        authentication_service=service,
    )


def test_registration_login_and_duplicate_username_responses(tmp_path) -> None:
    async def scenario() -> None:
        server = _authenticated_server(tmp_path)
        connection = FakeConnection()
        credentials = {"username": "Player_1", "password": "password123"}

        await server.handle_message(
            connection,
            json.dumps({"type": "register", **credentials}),
        )
        await server.handle_message(
            connection,
            json.dumps({"type": "register", **credentials}),
        )
        await server.handle_message(
            connection,
            json.dumps({"type": "login", **credentials}),
        )

        assert await connection.receive() == {
            "type": "registration_success",
            "username": "Player_1",
            "rating": 1200,
        }
        assert await connection.receive() == {"type": "username_taken"}
        assert await connection.receive() == {
            "type": "login_success",
            "username": "Player_1",
            "rating": 1200,
        }
        assert connection.outgoing.empty()

    asyncio.run(scenario())


def test_wrong_password_and_validation_return_structured_responses(tmp_path) -> None:
    async def scenario() -> None:
        server = _authenticated_server(tmp_path)
        connection = FakeConnection()

        await server.handle_message(
            connection,
            json.dumps(
                {
                    "type": "register",
                    "username": "Player_1",
                    "password": "password123",
                }
            ),
        )
        await connection.receive()
        await server.handle_message(
            connection,
            json.dumps(
                {
                    "type": "login",
                    "username": "Player_1",
                    "password": "wrong-password",
                }
            ),
        )
        await server.handle_message(
            connection,
            json.dumps(
                {"type": "register", "username": "x", "password": "short"}
            ),
        )

        assert await connection.receive() == {"type": "invalid_credentials"}
        assert await connection.receive() == {"type": "validation_error"}

    asyncio.run(scenario())


def test_unauthenticated_game_command_is_rejected(tmp_path) -> None:
    async def scenario() -> None:
        server = _authenticated_server(tmp_path)
        connection = FakeConnection()

        await server.handle_message(
            connection,
            json.dumps(
                {
                    "type": "move",
                    "source": {"row": 6, "column": 0},
                    "target": {"row": 5, "column": 0},
                }
            ),
        )

        assert await connection.receive() == {
            "type": "command_rejected",
            "reason": "authentication_required",
        }
        assert server.game_engine.get_motions() == ()

    asyncio.run(scenario())
