"""Authentication commands sent through a client transport."""

from __future__ import annotations

from concurrent.futures import Future
import queue
import threading
from typing import Any, Protocol


class MessageSender(Protocol):
    def send(self, message: dict[str, object]) -> Future[None]: ...


class AuthenticationClient:
    """Send credentials and wait for the matching authentication response."""

    def __init__(self, transport: MessageSender, responses: queue.Queue[dict[str, Any]], timeout: float) -> None:
        self._transport = transport
        self._responses = responses
        self._timeout = timeout
        self._lock = threading.Lock()

    def register(self, username: str, password: str) -> dict[str, Any]:
        """Register credentials and return the server response."""
        return self._authenticate("register", username, password)

    def login(self, username: str, password: str) -> dict[str, Any]:
        """Log in with credentials and return the server response."""
        return self._authenticate("login", username, password)

    def _authenticate(self, action: str, username: str, password: str) -> dict[str, Any]:
        with self._lock:
            self._transport.send({"type": action, "username": username, "password": password}).result(timeout=self._timeout)
            try:
                return self._responses.get(timeout=self._timeout)
            except queue.Empty as error:
                raise RuntimeError("Timed out waiting for authentication response.") from error
