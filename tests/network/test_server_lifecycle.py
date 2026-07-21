"""Lifecycle regression tests for extracted multiplayer server components."""

import asyncio

from app.game_engine_factory import GameEngineFactory
from events.game_events import MoveStartedEvent
from model.position import Position
from network.server.game_server import GameServer
from network.server.matches.session_manager import SessionManager
from tests.network.test_game_server import FakeConnection
from tests.network.test_server_reconnection import _matched_server


class BlockingConnection(FakeConnection):
    """Connection whose send remains pending until its task is cancelled."""

    def __init__(self) -> None:
        super().__init__()
        self.started = asyncio.Event()

    async def send(self, message: str) -> None:
        self.started.set()
        await asyncio.Future()


def test_close_cancels_pending_event_publications() -> None:
    async def scenario() -> None:
        sessions = SessionManager()
        connection = BlockingConnection()
        sessions.connect(connection)
        engine = GameEngineFactory.create()
        server = GameServer(engine, session_manager=sessions)

        engine.event_bus.publish(MoveStartedEvent(1, Position(6, 0), Position(5, 0)))
        await connection.started.wait()
        assert server._events._tasks

        await server.close()

        assert not server._events._tasks

    asyncio.run(scenario())


def test_recreating_server_with_same_engine_does_not_duplicate_events() -> None:
    async def scenario() -> None:
        engine = GameEngineFactory.create()
        first_connection = FakeConnection()
        first_sessions = SessionManager()
        first_sessions.connect(first_connection)
        first_server = GameServer(engine, session_manager=first_sessions)
        await first_server.close()

        second_connection = FakeConnection()
        second_sessions = SessionManager()
        second_sessions.connect(second_connection)
        second_server = GameServer(engine, session_manager=second_sessions)
        engine.event_bus.publish(MoveStartedEvent(1, Position(6, 0), Position(5, 0)))
        message = await asyncio.wait_for(second_connection.receive(), timeout=1)

        assert first_connection.outgoing.empty()
        assert message["type"] == "game_event"
        assert second_connection.outgoing.empty()
        await second_server.close()

    asyncio.run(scenario())


def test_close_cancels_reconnect_timeout_tasks(tmp_path) -> None:
    async def scenario() -> None:
        server, white, _, _, _ = await _matched_server(tmp_path)
        await server._handle_disconnect(white)
        assert server._match_sessions._disconnect_tasks

        await server.close()

        assert not server._match_sessions._disconnect_tasks
        assert not server._reconnect.is_paused()

    asyncio.run(scenario())


def test_completed_timeout_task_removes_itself(tmp_path) -> None:
    async def scenario() -> None:
        server, white, black, _, _ = await _matched_server(tmp_path, timeout=0.01)
        await server._handle_disconnect(white)
        await black.receive()
        await asyncio.sleep(0.04)

        assert not server._match_sessions._disconnect_tasks
        await server.close()

    asyncio.run(scenario())


def test_normal_game_completion_cancels_reconnect_timeouts(tmp_path) -> None:
    async def scenario() -> None:
        server, white, _, _, _ = await _matched_server(tmp_path)
        await server._handle_disconnect(white)
        assert server._match_sessions._disconnect_tasks

        await server._match_sessions.finish_game(None)

        assert not server._match_sessions._disconnect_tasks
        assert not server._reconnect.is_paused()
        await server.close()

    asyncio.run(scenario())


def test_failed_send_invokes_complete_disconnect_lifecycle(tmp_path) -> None:
    async def scenario() -> None:
        server, white, black, _, _ = await _matched_server(tmp_path)
        white.fail_send = True

        await server.broadcast({"type": "server_error"})

        assert server._sessions.color_for(white) is None
        assert server._authentication.lookup(white) is None
        assert server._matchmaking.state_for(white).value == "idle"
        assert server._reconnect.is_paused()
        received_types = {(await black.receive())["type"], (await black.receive())["type"]}
        assert received_types == {"server_error", "opponent_disconnected"}
        await server.close()

    asyncio.run(scenario())
