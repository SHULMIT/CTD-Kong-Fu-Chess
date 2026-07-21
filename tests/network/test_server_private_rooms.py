"""WebSocket boundary tests for authenticated private rooms."""

import asyncio
import json

from app.game_engine_factory import GameEngineFactory
from authentication.authentication_service import AuthenticationService
from authentication.sqlite_user_repository import SQLiteUserRepository
from network.server.game_server import GameServer
from rooms.private_room_service import PrivateRoomService, RoomStatus
from tests.network.test_game_server import FakeConnection
from tests.unit.test_authentication_service import FastTestHasher


def test_create_join_starts_exactly_one_existing_game_flow(tmp_path) -> None:
    async def scenario() -> None:
        server, creator, guest = await _server_and_users(tmp_path)
        await server.handle_message(creator, json.dumps({"type": "create_room"}))
        created = await creator.receive()
        assert created == {"type": "room_created", "room_code": "AB42KF"}

        await server.handle_message(
            guest,
            json.dumps({"type": "join_room", "room_code": "ab42kf"}),
        )
        creator_messages = [await creator.receive() for _ in range(5)]
        guest_messages = [await guest.receive() for _ in range(5)]
        assert creator_messages[0] == guest_messages[0] == {
            "type": "room_joined", "room_code": "AB42KF"
        }
        creator_match = next(item for item in creator_messages if item["type"] == "match_found")
        guest_match = next(item for item in guest_messages if item["type"] == "match_found")
        assert creator_match == guest_match
        assert creator_match["players"] == [
            {"username": "RoomOwner", "color": "white", "rating": 1200},
            {"username": "RoomGuest", "color": "black", "rating": 1200},
        ]
        assert sum(item["type"] == "match_found" for item in creator_messages) == 1

    asyncio.run(scenario())


def test_room_errors_cancel_and_disconnect_cleanup(tmp_path) -> None:
    async def scenario() -> None:
        server, creator, guest = await _server_and_users(tmp_path)
        await server.handle_message(
            guest, json.dumps({"type": "join_room", "room_code": "NONE00"})
        )
        assert await guest.receive() == {
            "type": "room_error", "reason": "unknown_room_code"
        }
        await server.handle_message(creator, json.dumps({"type": "create_room"}))
        await creator.receive()
        await server.handle_message(creator, json.dumps({"type": "create_room"}))
        assert (await creator.receive())["reason"] == "invalid_state"
        await server.handle_message(creator, json.dumps({"type": "cancel_room"}))
        assert await creator.receive() == {
            "type": "room_closed", "room_code": "AB42KF"
        }
        assert server._rooms.room("AB42KF").status is RoomStatus.CLOSED

        second_server, second_creator, _ = await _server_and_users(
            tmp_path / "second"
        )
        await second_server.handle_message(
            second_creator, json.dumps({"type": "create_room"})
        )
        await second_creator.receive()
        await second_server._handle_disconnect(second_creator)
        assert second_server._rooms.room("AB42KF").status is RoomStatus.CLOSED

    asyncio.run(scenario())


async def _server_and_users(tmp_path):
    repository = SQLiteUserRepository(tmp_path / "users.db")
    authentication = AuthenticationService(repository, FastTestHasher())
    authentication.initialize()
    authentication.register("RoomOwner", "password123")
    authentication.register("RoomGuest", "password123")
    server = GameServer(
        GameEngineFactory.create(),
        authentication_service=authentication,
        room_service=PrivateRoomService(code_factory=lambda _length: "AB42KF"),
    )
    creator, guest = FakeConnection(), FakeConnection()
    for connection, username in ((creator, "RoomOwner"), (guest, "RoomGuest")):
        await server.handle_message(
            connection,
            json.dumps({"type": "login", "username": username, "password": "password123"}),
        )
        await connection.receive()
    return server, creator, guest
