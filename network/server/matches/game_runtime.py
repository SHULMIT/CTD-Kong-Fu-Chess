"""Authoritative simulation loop isolated from WebSocket lifecycle."""

import asyncio
from collections.abc import Awaitable, Callable

from game.game_engine import GameEngine
from network.server.transport.game_snapshot_serializer import GameSnapshotSerializer, JsonValue


class GameRuntime:
    """Advances the engine under the command lock and publishes changed state."""

    def __init__(
        self,
        game_engine: GameEngine,
        serializer: GameSnapshotSerializer,
        command_lock: asyncio.Lock,
        broadcast: Callable[[dict[str, JsonValue]], Awaitable[None]],
        interval_seconds: float = 0.016,
    ) -> None:
        self._game_engine = game_engine
        self._serializer = serializer
        self._command_lock = command_lock
        self._broadcast = broadcast
        self._interval_seconds = interval_seconds

    async def run(self) -> None:
        """Continuously advance realtime state until the task is cancelled."""
        loop = asyncio.get_running_loop()
        previous_time = loop.time()
        while True:
            await asyncio.sleep(self._interval_seconds)
            current_time = loop.time()
            elapsed = max(1, int((current_time - previous_time) * 1000))
            previous_time = current_time
            async with self._command_lock:
                before = self._serializer.serialize(self._game_engine)
                self._game_engine.wait(elapsed)
                after = self._serializer.serialize(self._game_engine)
            if after != before:
                await self._broadcast({"type": "game_snapshot", "state": after})
