"""Compatibility facade for the multiplayer client components."""

from __future__ import annotations

from concurrent.futures import Future
import queue
from typing import Any

from model.piece import PieceColor
from model.position import Position
from network.authentication_client import AuthenticationClient
from network.client_session_state import ClientSessionState, MultiplayerClientState
from network.matchmaking_client import MatchmakingClient
from network.server_message_handler import ServerMessageHandler
from network.websocket_transport import WebSocketTransport, WebSocketTransportError


class NetworkClientError(RuntimeError):
    """Reports client failures without exposing component internals."""


class NetworkClient:
    """Stable UI-facing facade over transport, session, auth, and lobby services."""

    def __init__(self, uri: str = "ws://127.0.0.1:8765", connection_timeout: float = 5.0) -> None:
        self._connection_timeout = connection_timeout
        self._messages: queue.Queue[dict[str, Any]] = queue.Queue()
        self._authentication_responses: queue.Queue[dict[str, Any]] = queue.Queue()
        self._session = ClientSessionState()
        self._handler = ServerMessageHandler(self._session, self._messages, self._authentication_responses)
        self._transport = WebSocketTransport(uri, connection_timeout, self._handler.handle_raw, self._session.resume_token_value, self._session.consume_resume_completed)
        self._authentication = AuthenticationClient(self._transport, self._authentication_responses, connection_timeout)
        self._matchmaking = MatchmakingClient(self._transport, self._session)

    @property
    def assigned_color(self) -> PieceColor | None: return self._session.assigned_color
    @property
    def initial_snapshot(self) -> dict[str, Any] | None: return self._session.initial_snapshot
    @property
    def is_connected(self) -> bool: return self._transport.is_connected
    @property
    def username(self) -> str | None: return self._session.username
    @property
    def rating(self) -> int | None: return self._session.rating
    @property
    def matchmaking_state(self) -> MultiplayerClientState: return self._session.matchmaking_state
    @property
    def match_found(self) -> dict[str, Any] | None: return self._session.match_found
    @property
    def player_profiles(self) -> dict[str, Any] | None: return self._session.player_profiles

    # Private compatibility accessors retained for existing integrations/tests.
    _username = property(lambda self: self._session.username, lambda self, value: setattr(self._session, "username", value))
    _rating = property(lambda self: self._session.rating, lambda self, value: setattr(self._session, "rating", value))
    _assigned_color = property(lambda self: self._session.assigned_color, lambda self, value: setattr(self._session, "assigned_color", value))
    _matchmaking_state = property(lambda self: self._session.matchmaking_state, lambda self, value: setattr(self._session, "matchmaking_state", value))
    _resume_token = property(lambda self: self._session.resume_token, lambda self, value: setattr(self._session, "resume_token", value))

    def connect(self) -> None:
        """Open the multiplayer connection."""
        try:
            self._transport.connect()
        except WebSocketTransportError as error:
            raise NetworkClientError(str(error)) from error

    def disconnect(self) -> None:
        """Close the transport and clear local session data."""
        self._transport.disconnect()
        self._session.reset()
        self._drain_queue(self._messages)
        self._drain_queue(self._authentication_responses)

    def register(self, username: str, password: str) -> dict[str, Any]: return self._call(self._authentication.register, username, password)
    def login(self, username: str, password: str) -> dict[str, Any]: return self._call(self._authentication.login, username, password)
    def start_matchmaking(self) -> Future[None]: return self._call(self._matchmaking.start_matchmaking)
    def cancel_matchmaking(self) -> Future[None]: return self._call(self._matchmaking.cancel_matchmaking)
    def create_room(self) -> Future[None]: return self._call(self._matchmaking.create_room)
    def join_room(self, room_code: str) -> Future[None]: return self._call(self._matchmaking.join_room, room_code)
    def cancel_room(self) -> Future[None]: return self._call(self._matchmaking.cancel_room)
    def list_spectatable_games(self) -> Future[None]: return self._call(self._matchmaking.list_spectatable_games)
    def spectate_game(self, game_id: str) -> Future[None]: return self._call(self._matchmaking.spectate_game, game_id)
    def stop_spectating(self) -> Future[None]: return self._call(self._matchmaking.stop_spectating)

    def send(self, message: dict[str, object]) -> Future[None]: return self._call(self._transport.send, message)
    def send_move(self, source: Position, target: Position) -> Future[None]: return self.send({"type": "move", "source": self._serialize_position(source), "target": self._serialize_position(target)})
    def send_jump(self, position: Position) -> Future[None]: return self.send({"type": "jump", "position": self._serialize_position(position)})
    def request_legal_moves(self, position: Position) -> Future[None]: return self.send({"type": "legal_moves", "position": self._serialize_position(position)})
    def receive(self, timeout: float | None = None) -> dict[str, Any]: return self._messages.get(timeout=timeout)

    def poll_messages(self) -> tuple[dict[str, Any], ...]:
        """Drain decoded inbound messages for the UI thread."""
        messages: list[dict[str, Any]] = []
        while True:
            try: messages.append(self._messages.get_nowait())
            except queue.Empty: return tuple(messages)

    @staticmethod
    def _serialize_position(position: Position) -> dict[str, int]: return {"row": position.row, "column": position.column}
    @staticmethod
    def _drain_queue(target: queue.Queue[dict[str, Any]]) -> None:
        while True:
            try: target.get_nowait()
            except queue.Empty: return
    @staticmethod
    def _call(function: Any, *args: Any) -> Any:
        try: return function(*args)
        except (RuntimeError, WebSocketTransportError) as error: raise NetworkClientError(str(error)) from error
