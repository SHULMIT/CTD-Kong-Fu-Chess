"""Thread-safe WebSocket client for the local multiplayer server."""

import asyncio
from concurrent.futures import Future
import json
import queue
import threading
from enum import Enum
from typing import Any

from model.piece import PieceColor
from model.position import Position
from websockets.asyncio.client import ClientConnection, connect


class NetworkClientError(RuntimeError):
    """Reports connection failures without exposing transport internals."""


class MultiplayerClientState(Enum):
    """Client presentation state; the server remains authoritative."""

    IDLE = "idle"
    SEARCHING = "searching"
    ROOM_WAITING = "room_waiting"
    MATCHED = "matched"
    IN_GAME = "in_game"
    SPECTATING = "spectating"


class NetworkClient:
    """Owns one background WebSocket connection and its message queues."""

    def __init__(
        self,
        uri: str = "ws://127.0.0.1:8765",
        connection_timeout: float = 5.0,
    ) -> None:
        self._uri = uri
        self._connection_timeout = connection_timeout
        self._messages: queue.Queue[dict[str, Any]] = queue.Queue()
        self._authentication_responses: queue.Queue[dict[str, Any]] = queue.Queue()
        self._connected = threading.Event()
        self._ready = threading.Event()
        self._thread: threading.Thread | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._connection: ClientConnection | None = None
        self._assigned_color: PieceColor | None = None
        self._initial_snapshot: dict[str, Any] | None = None
        self._connection_error: str | None = None
        self._username: str | None = None
        self._rating: int | None = None
        self._matchmaking_state = MultiplayerClientState.IDLE
        self._match_found: dict[str, Any] | None = None
        self._resume_token: str | None = None
        self._intentional_disconnect = False
        self._resume_completed = False
        self._player_profiles: dict[str, Any] | None = None

    @property
    def assigned_color(self) -> PieceColor | None:
        """Return the color assigned by the server after connection."""
        return self._assigned_color

    @property
    def initial_snapshot(self) -> dict[str, Any] | None:
        """Return the first authoritative snapshot received from the server."""
        return self._initial_snapshot

    @property
    def is_connected(self) -> bool:
        """Return whether the background transport is currently connected."""
        return self._connected.is_set()

    @property
    def username(self) -> str | None:
        """Return the authenticated username, if login succeeded."""
        return self._username

    @property
    def rating(self) -> int | None:
        """Return the rating supplied by the server at login."""
        return self._rating

    @property
    def matchmaking_state(self) -> MultiplayerClientState:
        """Return the latest state acknowledged by the server."""
        return self._matchmaking_state

    @property
    def match_found(self) -> dict[str, Any] | None:
        """Return the latest authoritative match payload, if any."""
        return self._match_found

    @property
    def player_profiles(self) -> dict[str, Any] | None:
        """Return the latest authoritative profiles message."""
        return self._player_profiles

    def connect(self) -> None:
        """Open the transport; authentication is performed separately."""
        if self._thread is not None and self._thread.is_alive():
            return

        self._reset_connection_state()
        self._intentional_disconnect = False
        self._thread = threading.Thread(
            target=self._run_background_loop,
            name="kung-fu-chess-network-client",
            daemon=True,
        )
        self._thread.start()
        if not self._connected.wait(self._connection_timeout):
            self.disconnect()
            raise NetworkClientError("Timed out waiting for the game server.")
        if self._connection_error is not None:
            self.disconnect()
            raise NetworkClientError(self._connection_error)

    def register(self, username: str, password: str) -> dict[str, Any]:
        """Send registration credentials and return the structured response."""
        return self._authenticate("register", username, password)

    def login(self, username: str, password: str) -> dict[str, Any]:
        """Authenticate; joining a game is an explicit later user action."""
        return self._authenticate("login", username, password)

    def start_matchmaking(self) -> Future[None]:
        """Ask the server to queue this authenticated user."""
        if self._matchmaking_state is not MultiplayerClientState.IDLE:
            raise NetworkClientError("The client is already matchmaking or in a game.")
        self._matchmaking_state = MultiplayerClientState.SEARCHING
        try:
            return self.send({"type": "start_matchmaking"})
        except Exception:
            self._matchmaking_state = MultiplayerClientState.IDLE
            raise

    def cancel_matchmaking(self) -> Future[None]:
        """Ask the server to remove this user from the queue."""
        return self.send({"type": "cancel_matchmaking"})

    def create_room(self) -> Future[None]:
        """Request a new server-owned private room."""
        if self._matchmaking_state is not MultiplayerClientState.IDLE:
            raise NetworkClientError("The client is not idle.")
        return self.send({"type": "create_room"})

    def join_room(self, room_code: str) -> Future[None]:
        """Request entry to a private room by its short code."""
        if self._matchmaking_state is not MultiplayerClientState.IDLE:
            raise NetworkClientError("The client is not idle.")
        return self.send({"type": "join_room", "room_code": room_code})

    def cancel_room(self) -> Future[None]:
        """Close the private room currently owned by this client."""
        return self.send({"type": "cancel_room"})

    def list_spectatable_games(self) -> Future[None]:
        """Request active games available for read-only viewing."""
        return self.send({"type": "list_spectatable_games"})

    def spectate_game(self, game_id: str) -> Future[None]:
        """Request read-only access to an active game."""
        return self.send({"type": "spectate_game", "game_id": game_id})

    def stop_spectating(self) -> Future[None]:
        """Leave a spectator view without affecting the game."""
        return self.send({"type": "stop_spectating"})

    def send(self, message: dict[str, object]) -> Future[None]:
        """Schedule one JSON-safe message for transmission to the server."""
        loop = self._loop
        if loop is None or not self.is_connected:
            raise NetworkClientError("The multiplayer client is not connected.")
        return asyncio.run_coroutine_threadsafe(
            self._send_message(message),
            loop,
        )

    def send_move(self, source: Position, target: Position) -> Future[None]:
        """Send a move command using the shared network message format."""
        return self.send(
            {
                "type": "move",
                "source": self._serialize_position(source),
                "target": self._serialize_position(target),
            }
        )

    def send_jump(self, position: Position) -> Future[None]:
        """Send a jump command using the shared network message format."""
        return self.send(
            {
                "type": "jump",
                "position": self._serialize_position(position),
            }
        )

    def request_legal_moves(self, position: Position) -> Future[None]:
        """Request authoritative legal destinations for one selected piece."""
        return self.send(
            {
                "type": "legal_moves",
                "position": self._serialize_position(position),
            }
        )

    def receive(self, timeout: float | None = None) -> dict[str, Any]:
        """Return the next server message from the thread-safe inbound queue."""
        return self._messages.get(timeout=timeout)

    def poll_messages(self) -> tuple[dict[str, Any], ...]:
        """Drain messages for safe processing by the caller's UI thread."""
        messages = []
        while True:
            try:
                messages.append(self._messages.get_nowait())
            except queue.Empty:
                return tuple(messages)

    def disconnect(self) -> None:
        """Close the WebSocket connection and stop its background thread."""
        self._intentional_disconnect = True
        loop = self._loop
        connection = self._connection
        if loop is not None and connection is not None and loop.is_running():
            future = asyncio.run_coroutine_threadsafe(connection.close(), loop)
            try:
                future.result(timeout=self._connection_timeout)
            except Exception:
                pass

        thread = self._thread
        if thread is not None and thread is not threading.current_thread():
            thread.join(timeout=self._connection_timeout)
        self._connected.clear()
        self._thread = None

    def _run_background_loop(self) -> None:
        try:
            asyncio.run(self._connection_loop())
        except Exception:
            self._connection_error = "Unable to connect to the game server."
            self._ready.set()
        finally:
            self._connected.clear()
            self._connection = None
            self._loop = None

    async def _connection_loop(self) -> None:
        self._loop = asyncio.get_running_loop()
        reconnect_deadline: float | None = None
        while not self._intentional_disconnect:
            try:
                async with connect(self._uri, proxy=None) as connection:
                    self._connection = connection
                    self._connected.set()
                    if reconnect_deadline is not None and self._resume_token is not None:
                        await connection.send(
                            json.dumps(
                                {"type": "resume_session", "token": self._resume_token}
                            )
                        )
                    async for raw_message in connection:
                        self._receive_message(raw_message)
            except Exception:
                if reconnect_deadline is None:
                    raise
            finally:
                self._connected.clear()
                self._connection = None
            if self._intentional_disconnect or self._resume_token is None:
                return
            if self._resume_completed:
                reconnect_deadline = None
                self._resume_completed = False
            if reconnect_deadline is None:
                reconnect_deadline = self._loop.time() + 20.0
                self._messages.put({"type": "connection_lost"})
            if self._loop.time() >= reconnect_deadline:
                self._messages.put({"type": "session_resume_rejected", "reason": "timeout"})
                return
            await asyncio.sleep(0.5)

    async def _send_message(self, message: dict[str, object]) -> None:
        connection = self._connection
        if connection is None:
            raise NetworkClientError("The multiplayer client is not connected.")
        await connection.send(json.dumps(message))

    def _receive_message(self, raw_message: str | bytes) -> None:
        try:
            message = json.loads(raw_message)
        except (json.JSONDecodeError, UnicodeDecodeError):
            message = {"type": "server_error"}

        if not isinstance(message, dict):
            message = {"type": "server_error"}
        self._capture_handshake(message)
        self._messages.put(message)

    def _capture_handshake(self, message: dict[str, Any]) -> None:
        message_type = message.get("type")
        if message_type in {
            "registration_success",
            "login_success",
            "username_taken",
            "invalid_credentials",
            "validation_error",
            "server_error",
            "connection_rejected",
        }:
            if message_type == "login_success":
                self._username = str(message.get("username"))
                rating = message.get("rating")
                self._rating = rating if type(rating) is int else None
            self._authentication_responses.put(message)
        if message_type == "connection_accepted":
            color = message.get("color")
            try:
                self._assigned_color = PieceColor[str(color).upper()]
            except KeyError:
                self._connection_error = "Server returned an invalid color."
                self._ready.set()
            self._matchmaking_state = MultiplayerClientState.IN_GAME
        elif message_type == "connection_rejected":
            reason = str(message.get("reason", "connection_rejected"))
            self._connection_error = f"Server rejected connection: {reason}."
            self._ready.set()
        elif message_type == "game_snapshot":
            state = message.get("state")
            if isinstance(state, dict):
                self._initial_snapshot = state
                self._ready.set()
        elif message_type == "rating_updated" and self._assigned_color is not None:
            for profile in message.get("players", []):
                if profile.get("color") == self._assigned_color.name.lower():
                    rating = profile.get("rating")
                    if type(rating) is int:
                        self._rating = rating
        elif message_type == "matchmaking_queued":
            self._matchmaking_state = MultiplayerClientState.SEARCHING
            rating = message.get("rating")
            if type(rating) is int:
                self._rating = rating
        elif message_type == "matchmaking_canceled":
            self._matchmaking_state = MultiplayerClientState.IDLE
        elif message_type == "match_found":
            self._matchmaking_state = MultiplayerClientState.MATCHED
            self._match_found = message
        elif message_type == "room_created":
            self._matchmaking_state = MultiplayerClientState.ROOM_WAITING
        elif message_type == "room_closed":
            self._matchmaking_state = MultiplayerClientState.IDLE
        elif message_type == "spectating_started":
            self._matchmaking_state = MultiplayerClientState.SPECTATING
        elif message_type == "spectating_stopped":
            self._matchmaking_state = MultiplayerClientState.IDLE
        elif message_type == "player_profiles":
            self._player_profiles = message
        elif message_type == "session_resume_token":
            token = message.get("token")
            if isinstance(token, str):
                self._resume_token = token
        elif message_type == "session_resumed":
            color = message.get("color")
            try:
                self._assigned_color = PieceColor[str(color).upper()]
            except KeyError:
                return
            self._matchmaking_state = MultiplayerClientState.IN_GAME
            self._resume_completed = True

    def _reset_connection_state(self) -> None:
        self._connected.clear()
        self._ready.clear()
        self._assigned_color = None
        self._initial_snapshot = None
        self._connection_error = None
        self._username = None
        self._rating = None
        self._matchmaking_state = MultiplayerClientState.IDLE
        self._match_found = None
        self._player_profiles = None
        self._resume_token = None
        while not self._authentication_responses.empty():
            try:
                self._authentication_responses.get_nowait()
            except queue.Empty:
                break

    def _authenticate(
        self,
        action: str,
        username: str,
        password: str,
    ) -> dict[str, Any]:
        self.send(
            {
                "type": action,
                "username": username,
                "password": password,
            }
        ).result(timeout=self._connection_timeout)
        try:
            return self._authentication_responses.get(
                timeout=self._connection_timeout
            )
        except queue.Empty as error:
            raise NetworkClientError(
                "Timed out waiting for authentication response."
            ) from error

    @staticmethod
    def _serialize_position(position: Position) -> dict[str, int]:
        return {"row": position.row, "column": position.column}
