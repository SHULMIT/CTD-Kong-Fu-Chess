"""Focused async tests for the authoritative local game server."""

import asyncio
import json
from typing import Any

from app.game_engine_factory import GameEngineFactory
from events.game_events import MoveStartedEvent
from model.position import Position
from network.server.game_server import GameServer
from network.server.matches.session_manager import SessionManager


class FakeConnection:
    """Queue-backed connection fake with deterministic synchronization."""

    _DISCONNECT = object()

    def __init__(self, fail_send: bool = False) -> None:
        self._incoming: asyncio.Queue[str | object] = asyncio.Queue()
        self.outgoing: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        self.fail_send = fail_send

    def __aiter__(self) -> "FakeConnection":
        return self

    async def __anext__(self) -> str:
        message = await self._incoming.get()
        if message is self._DISCONNECT:
            raise StopAsyncIteration
        return str(message)

    async def send(self, message: str) -> None:
        if self.fail_send:
            raise OSError("connection closed")
        await self.outgoing.put(json.loads(message))

    async def receive(self) -> dict[str, Any]:
        return await self.outgoing.get()

    async def feed(self, message: str) -> None:
        await self._incoming.put(message)

    async def disconnect(self) -> None:
        await self._incoming.put(self._DISCONNECT)


def _message(message_type: str, connection: FakeConnection) -> dict[str, Any]:
    messages = list(connection.outgoing._queue)
    return next(item for item in messages if item["type"] == message_type)


def test_accepted_client_receives_color_and_initial_snapshot() -> None:
    async def scenario() -> None:
        server = GameServer(GameEngineFactory.create())
        connection = FakeConnection()
        await connection.disconnect()

        await server.handle_client(connection)

        accepted = await connection.receive()
        snapshot = await connection.receive()
        assert accepted == {"type": "connection_accepted", "color": "white"}
        assert snapshot["type"] == "game_snapshot"
        assert snapshot["state"]["board"]["pieces"]

    asyncio.run(scenario())


def test_third_client_is_rejected() -> None:
    async def scenario() -> None:
        sessions = SessionManager()
        sessions.connect(object())
        sessions.connect(object())
        server = GameServer(
            GameEngineFactory.create(),
            session_manager=sessions,
        )
        connection = FakeConnection()

        await server.handle_client(connection)

        assert await connection.receive() == {
            "type": "connection_rejected",
            "reason": "game_full",
        }

    asyncio.run(scenario())


def test_valid_move_from_owner_is_executed_and_broadcast() -> None:
    async def scenario() -> None:
        sessions = SessionManager()
        connection = FakeConnection()
        sessions.connect(connection)
        engine = GameEngineFactory.create()
        server = GameServer(engine, session_manager=sessions)
        message = json.dumps(
            {
                "type": "move",
                "source": {"row": 6, "column": 0},
                "target": {"row": 5, "column": 0},
            }
        )

        await server.handle_message(connection, message)

        assert _message("command_accepted", connection)["command"] == "move"
        assert _message("game_snapshot", connection)["state"]["motions"]
        assert engine.get_motions()

    asyncio.run(scenario())


def test_move_for_opponents_piece_is_rejected() -> None:
    async def scenario() -> None:
        sessions = SessionManager()
        connection = FakeConnection()
        sessions.connect(connection)
        engine = GameEngineFactory.create()
        server = GameServer(engine, session_manager=sessions)
        message = json.dumps(
            {
                "type": "move",
                "source": {"row": 1, "column": 0},
                "target": {"row": 2, "column": 0},
            }
        )

        await server.handle_message(connection, message)

        assert await connection.receive() == {
            "type": "command_rejected",
            "reason": "not_your_piece",
        }
        assert engine.get_motions() == ()

    asyncio.run(scenario())


def test_legal_moves_request_returns_authoritative_destinations() -> None:
    async def scenario() -> None:
        sessions = SessionManager()
        connection = FakeConnection()
        sessions.connect(connection)
        server = GameServer(
            GameEngineFactory.create(),
            session_manager=sessions,
        )
        message = json.dumps(
            {
                "type": "legal_moves",
                "position": {"row": 6, "column": 0},
            }
        )

        await server.handle_message(connection, message)

        assert await connection.receive() == {
            "type": "legal_moves",
            "source": {"row": 6, "column": 0},
            "positions": [
                {"row": 4, "column": 0},
                {"row": 5, "column": 0},
            ],
        }

    asyncio.run(scenario())


def test_legal_moves_rejects_opponent_piece_and_missing_piece() -> None:
    async def scenario() -> None:
        sessions = SessionManager()
        connection = FakeConnection()
        sessions.connect(connection)
        server = GameServer(
            GameEngineFactory.create(),
            session_manager=sessions,
        )

        await server.handle_message(
            connection,
            json.dumps(
                {
                    "type": "legal_moves",
                    "position": {"row": 1, "column": 0},
                }
            ),
        )
        await server.handle_message(
            connection,
            json.dumps(
                {
                    "type": "legal_moves",
                    "position": {"row": 4, "column": 4},
                }
            ),
        )

        assert await connection.receive() == {
            "type": "command_rejected",
            "reason": "not_your_piece",
        }
        assert await connection.receive() == {
            "type": "command_rejected",
            "reason": "missing_piece",
        }

    asyncio.run(scenario())


def test_invalid_json_and_malformed_command_return_structured_errors() -> None:
    async def scenario() -> None:
        sessions = SessionManager()
        connection = FakeConnection()
        sessions.connect(connection)
        server = GameServer(
            GameEngineFactory.create(),
            session_manager=sessions,
        )

        await server.handle_message(connection, "not-json")
        await server.handle_message(connection, '{"type": "move"}')

        assert await connection.receive() == {
            "type": "command_rejected",
            "reason": "invalid_json",
        }
        assert await connection.receive() == {
            "type": "command_rejected",
            "reason": "malformed_command",
        }

    asyncio.run(scenario())


def test_illegal_game_command_returns_domain_rejection() -> None:
    async def scenario() -> None:
        sessions = SessionManager()
        connection = FakeConnection()
        sessions.connect(connection)
        server = GameServer(
            GameEngineFactory.create(),
            session_manager=sessions,
        )
        message = json.dumps(
            {
                "type": "move",
                "source": {"row": 6, "column": 0},
                "target": {"row": 3, "column": 0},
            }
        )

        await server.handle_message(connection, message)

        response = await connection.receive()
        assert response["type"] == "command_rejected"
        assert response["reason"] == "illegal_piece_move"

    asyncio.run(scenario())


def test_game_event_is_broadcast_to_both_clients() -> None:
    async def scenario() -> None:
        sessions = SessionManager()
        first = FakeConnection()
        second = FakeConnection()
        sessions.connect(first)
        sessions.connect(second)
        engine = GameEngineFactory.create()
        server = GameServer(engine, session_manager=sessions)

        engine.event_bus.publish(
            MoveStartedEvent(1, Position(6, 0), Position(5, 0))
        )

        first_message, second_message = await asyncio.gather(
            first.receive(), second.receive()
        )
        assert first_message == second_message
        assert first_message["type"] == "game_event"
        assert first_message["event_id"] == 1
        assert first_message["event"]["type"] == "move_started"

    asyncio.run(scenario())


def test_failed_client_send_does_not_break_broadcast() -> None:
    async def scenario() -> None:
        sessions = SessionManager()
        failed = FakeConnection(fail_send=True)
        healthy = FakeConnection()
        sessions.connect(failed)
        sessions.connect(healthy)
        server = GameServer(
            GameEngineFactory.create(),
            session_manager=sessions,
        )

        await server.broadcast({"type": "server_error"})

        assert await healthy.receive() == {"type": "server_error"}
        assert sessions.color_for(failed) is None

    asyncio.run(scenario())


def test_two_clients_share_one_authoritative_engine() -> None:
    engine = GameEngineFactory.create()
    server = GameServer(engine)

    assert server.game_engine is engine


def test_simultaneous_commands_are_serialized_by_command_lock() -> None:
    async def scenario() -> None:
        sessions = SessionManager()
        white = FakeConnection()
        black = FakeConnection()
        sessions.connect(white)
        sessions.connect(black)
        engine = GameEngineFactory.create()
        server = GameServer(engine, session_manager=sessions)
        await server._command_lock.acquire()
        white_message = json.dumps(
            {
                "type": "jump",
                "position": {"row": 6, "column": 0},
            }
        )
        black_message = json.dumps(
            {
                "type": "jump",
                "position": {"row": 1, "column": 0},
            }
        )
        first_task = asyncio.create_task(
            server.handle_message(white, white_message)
        )
        second_task = asyncio.create_task(
            server.handle_message(black, black_message)
        )

        await asyncio.sleep(0)
        assert white.outgoing.empty()
        assert black.outgoing.empty()
        server._command_lock.release()
        await asyncio.gather(first_task, second_task)

        assert _message("command_accepted", white)["command"] == "jump"
        assert _message("command_accepted", black)["command"] == "jump"

    asyncio.run(scenario())
