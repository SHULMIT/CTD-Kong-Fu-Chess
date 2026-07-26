"""Background WebSocket transport independent of application protocol state."""

from __future__ import annotations

import asyncio
from concurrent.futures import Future
import json
import threading
from collections.abc import Callable

from websockets.asyncio.client import ClientConnection, connect


class WebSocketTransportError(RuntimeError):
    """Report transport failures without exposing WebSocket implementation details."""


class WebSocketTransport:
    """Own a WebSocket, its event loop, and reconnect/session-resume mechanics."""

    def __init__(
        self,
        uri: str,
        connection_timeout: float,
        on_message: Callable[[str | bytes], None],
        resume_token: Callable[[], str | None],
        resume_completed: Callable[[], bool],
    ) -> None:
        self._uri = uri
        self._connection_timeout = connection_timeout
        self._on_message = on_message
        self._resume_token = resume_token
        self._resume_completed = resume_completed
        self._connected = threading.Event()
        self._thread: threading.Thread | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._connection: ClientConnection | None = None
        self._connection_error: str | None = None
        self._intentional_disconnect = False

    @property
    def is_connected(self) -> bool:
        """Whether the underlying socket is currently connected."""
        return self._connected.is_set()

    def connect(self) -> None:
        """Open the background connection, failing on initial connection failure."""
        if self._thread is not None and self._thread.is_alive():
            if self._intentional_disconnect:
                raise WebSocketTransportError("The multiplayer client is still shutting down.")
            return
        self._connection_error = None
        self._intentional_disconnect = False
        self._thread = threading.Thread(target=self._run_background_loop, name="kung-fu-chess-network-client", daemon=True)
        self._thread.start()
        if not self._connected.wait(self._connection_timeout):
            self.disconnect()
            raise WebSocketTransportError(self._connection_error or "Timed out waiting for the game server.")

    def disconnect(self) -> None:
        """Close the socket and join the IO thread."""
        self._intentional_disconnect = True
        loop, connection = self._loop, self._connection
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
        self._thread = thread if thread is not None and thread.is_alive() else None

    def send(self, message: dict[str, object]) -> Future[None]:
        """Schedule a JSON-safe protocol message for delivery."""
        loop = self._loop
        if loop is None or not self.is_connected:
            raise WebSocketTransportError("The multiplayer client is not connected.")
        return asyncio.run_coroutine_threadsafe(self._send_message(message), loop)

    def _run_background_loop(self) -> None:
        try:
            asyncio.run(self._connection_loop())
        except Exception:
            self._connection_error = "Unable to connect to the game server."
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
                    token = self._resume_token()
                    if reconnect_deadline is not None and token is not None:
                        await connection.send(json.dumps({"type": "resume_session", "token": token}))
                    async for raw_message in connection:
                        self._on_message(raw_message)
            except Exception:
                if reconnect_deadline is None:
                    raise
            finally:
                self._connected.clear()
                self._connection = None
            if self._intentional_disconnect or self._resume_token() is None:
                return
            if self._resume_completed():
                reconnect_deadline = None
            if reconnect_deadline is None:
                reconnect_deadline = self._loop.time() + 20.0
                self._on_message(json.dumps({"type": "connection_lost"}))
            if self._loop.time() >= reconnect_deadline:
                self._on_message(json.dumps({"type": "session_resume_rejected", "reason": "timeout"}))
                return
            await asyncio.sleep(0.5)

    async def _send_message(self, message: dict[str, object]) -> None:
        connection = self._connection
        if connection is None:
            raise WebSocketTransportError("The multiplayer client is not connected.")
        await connection.send(json.dumps(message))
