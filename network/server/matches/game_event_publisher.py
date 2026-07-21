"""Game-event subscription, serialization, and asynchronous publication."""

import asyncio
import logging
from collections.abc import Awaitable, Callable

from events.event import Event
from events.game_events import (
    GameOverEvent,
    JumpCompletedEvent,
    JumpStartedEvent,
    MoveCompletedEvent,
    MoveStartedEvent,
    ScoreChangedEvent,
)
from events.subscription import Subscription
from game.game_engine import GameEngine
from model.piece import PieceColor
from network.server.transport.game_event_serializer import GameEventSerializer
from network.server.transport.game_snapshot_serializer import JsonValue


class GameEventPublisher:
    """Turns engine events into ordered network events and completion callbacks."""

    _OBSERVED_TYPES = (
        MoveStartedEvent,
        MoveCompletedEvent,
        JumpStartedEvent,
        JumpCompletedEvent,
        ScoreChangedEvent,
        GameOverEvent,
    )

    def __init__(
        self,
        game_engine: GameEngine,
        serializer: GameEventSerializer,
        broadcast: Callable[[dict[str, JsonValue]], Awaitable[None]],
        finish_game: Callable[[PieceColor | None], Awaitable[None]],
        game_id_provider: Callable[[], str],
        logger: logging.Logger,
    ) -> None:
        self._serializer = serializer
        self._broadcast = broadcast
        self._finish_game = finish_game
        self._game_id_provider = game_id_provider
        self._logger = logger
        self._loop: asyncio.AbstractEventLoop | None = None
        self._tasks: set[asyncio.Task[None]] = set()
        self._subscriptions: list[Subscription] = []
        self._event_bus = game_engine.event_bus
        self._closed = False
        self._next_event_id = 1
        self._completed_games: set[str] = set()
        for event_type in self._OBSERVED_TYPES:
            self._subscriptions.append(
                self._event_bus.subscribe(event_type, self._on_event)
            )

    def set_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop

    def _on_event(self, event: Event) -> None:
        if self._closed:
            return
        message: dict[str, JsonValue] = {
            "type": "game_event",
            "event_id": self._next_event_id,
            "event": self._serializer.serialize(event),
        }
        self._next_event_id += 1
        loop = self._loop
        if loop is None:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                self._logger.warning("Cannot broadcast game event without a running loop")
                return
            self._loop = loop
        self._schedule(loop, self._broadcast(message))
        if isinstance(event, GameOverEvent):
            game_id = self._game_id_provider()
            if game_id in self._completed_games:
                return
            self._completed_games.add(game_id)
            self._logger.info(
                "game_over",
                extra={"event_type": "game_over", "game_id": game_id},
            )
            self._schedule(loop, self._finish_game(event.winner))

    async def close(self) -> None:
        """Stop observing engine events and settle all pending publications."""
        if self._closed:
            return
        self._closed = True
        for subscription in self._subscriptions:
            self._event_bus.unsubscribe(subscription)
        self._subscriptions.clear()
        tasks = tuple(self._tasks)
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        self._tasks.clear()

    def _schedule(
        self,
        loop: asyncio.AbstractEventLoop,
        operation: Awaitable[None],
    ) -> None:
        task = loop.create_task(operation)
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
