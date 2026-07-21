"""JSON encoding and WebSocket delivery for server components."""

import asyncio
import json
import logging
from collections.abc import Awaitable, Callable, Iterable
from typing import Protocol, cast

from network.server.transport.game_snapshot_serializer import JsonValue


class MessageConnection(Protocol):
    """Minimum connection interface required for outgoing messages."""

    async def send(self, message: str) -> None: ...


class ClientMessenger:
    """Sends JSON messages and broadcasts to caller-supplied recipients."""

    def __init__(
        self,
        recipient_provider: Callable[[], Iterable[object]],
        logger: logging.Logger,
    ) -> None:
        self._recipient_provider = recipient_provider
        self._logger = logger
        self._connection_failure_handler: (
            Callable[[object], Awaitable[None]] | None
        ) = None
        self._failing_connections: set[object] = set()

    def set_connection_failure_handler(
        self,
        handler: Callable[[object], Awaitable[None]],
    ) -> None:
        """Install the complete connection lifecycle cleanup callback."""
        self._connection_failure_handler = handler

    async def send(
        self,
        connection: MessageConnection,
        message: dict[str, JsonValue],
    ) -> None:
        """Encode and send one JSON-safe message."""
        await self.send_encoded(connection, json.dumps(message))

    async def send_encoded(
        self,
        connection: MessageConnection,
        encoded_message: str,
    ) -> None:
        """Send pre-encoded JSON and consistently handle failed sockets."""
        try:
            await connection.send(encoded_message)
        except Exception:
            self._logger.warning(
                "Removed client after a failed WebSocket send",
                exc_info=True,
            )
            await self._handle_failed_connection(connection)

    async def _handle_failed_connection(self, connection: object) -> None:
        if connection in self._failing_connections:
            return
        self._failing_connections.add(connection)
        try:
            if self._connection_failure_handler is not None:
                await self._connection_failure_handler(connection)
            else:
                self._logger.error(
                    "No connection failure handler is installed",
                    extra={"event_type": "connection_cleanup_unavailable"},
                )
        finally:
            self._failing_connections.discard(connection)

    async def broadcast(self, message: dict[str, JsonValue]) -> None:
        """Send one message once to every current unique recipient."""
        recipients = tuple(dict.fromkeys(self._recipient_provider()))
        if not recipients:
            return
        encoded = json.dumps(message)
        await asyncio.gather(
            *(
                self.send_encoded(cast(MessageConnection, client), encoded)
                for client in recipients
            )
        )

    async def reject(self, connection: MessageConnection, reason: str) -> None:
        """Send the stable command-rejection envelope."""
        self._logger.info("Rejected client command: %s", reason)
        await self.send(connection, self.rejection(reason))

    @staticmethod
    def rejection(reason: str) -> dict[str, JsonValue]:
        return {"type": "command_rejected", "reason": reason}
