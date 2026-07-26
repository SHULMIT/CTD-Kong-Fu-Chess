"""Focused tests for the components behind the NetworkClient facade."""

from concurrent.futures import Future
import json
import queue

import pytest

from model.piece import PieceColor
from network.authentication_client import AuthenticationClient
from network.client_session_state import ClientSessionState, MultiplayerClientState
from network.matchmaking_client import MatchmakingClient
from network.server_message_handler import ServerMessageHandler


class FakeTransport:
    """Record messages while presenting the transport sending interface."""

    def __init__(self) -> None:
        self.messages: list[dict[str, object]] = []

    def send(self, message: dict[str, object]) -> Future[None]:
        self.messages.append(message)
        future: Future[None] = Future()
        future.set_result(None)
        return future


def test_handler_updates_session_and_routes_authentication_message() -> None:
    session = ClientSessionState()
    messages: queue.Queue[dict] = queue.Queue()
    authentication_responses: queue.Queue[dict] = queue.Queue()
    handler = ServerMessageHandler(session, messages, authentication_responses)

    handler.handle_raw(json.dumps({"type": "login_success", "username": "Noa", "rating": 1216}))
    handler.handle({"type": "connection_accepted", "color": "white"})
    handler.handle({"type": "game_snapshot", "state": {"board": {}}})

    assert session.username == "Noa"
    assert session.rating == 1216
    assert session.assigned_color is PieceColor.WHITE
    assert session.initial_snapshot == {"board": {}}
    assert authentication_responses.get_nowait()["type"] == "login_success"
    assert [messages.get_nowait()["type"] for _ in range(3)] == [
        "login_success", "connection_accepted", "game_snapshot",
    ]


def test_authentication_client_sends_credentials_and_waits_for_response() -> None:
    transport = FakeTransport()
    responses: queue.Queue[dict] = queue.Queue()
    responses.put({"type": "registration_success"})

    response = AuthenticationClient(transport, responses, timeout=0.1).register("Noa", "secret")

    assert response == {"type": "registration_success"}
    assert transport.messages == [{"type": "register", "username": "Noa", "password": "secret"}]


def test_matchmaking_client_requires_idle_state_and_updates_optimistically() -> None:
    transport = FakeTransport()
    session = ClientSessionState()
    client = MatchmakingClient(transport, session)

    client.start_matchmaking().result()

    assert session.matchmaking_state is MultiplayerClientState.SEARCHING
    assert transport.messages == [{"type": "start_matchmaking"}]
    with pytest.raises(RuntimeError, match="not idle"):
        client.create_room()
