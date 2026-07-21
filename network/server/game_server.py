"""Thin WebSocket lifecycle façade for the authoritative multiplayer server."""

import asyncio
from collections.abc import AsyncIterator
import logging
from typing import Protocol

from authentication.authentication_service import AuthenticationService
from game.game_engine import GameEngine
from matchmaking.matchmaking_service import Match, MatchmakingService
from model.piece import PieceColor
from network.server.authentication_handler import AuthenticationHandler
from network.server.transport.client_message_router import ClientMessageRouter
from network.server.transport.client_messenger import ClientMessenger
from network.server.transport.command_parser import CommandParser
from network.server.matches.game_command_handler import GameCommandHandler
from network.server.matches.game_event_publisher import GameEventPublisher
from network.server.transport.game_event_serializer import GameEventSerializer
from network.server.matches.game_runtime import GameRuntime
from network.server.transport.game_snapshot_serializer import GameSnapshotSerializer, JsonValue
from network.server.lobby_handler import LobbyHandler
from network.server.matches.match_session_coordinator import MatchSessionCoordinator
from network.server.matches.rating_finalizer import RatingFinalizer
from network.server.matches.reconnect_session_service import ReconnectSessionService
from network.server.matches.session_manager import SessionManager
from network.server.spectator_handler import SpectatorHandler
from rating.persistent_rating_service import PersistentRatingService
from rooms.private_room_service import PrivateRoomService
from spectators.spectator_service import SpectatorService
from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosed


class ClientConnection(Protocol):
    """Minimum bidirectional behavior required from a WebSocket connection."""

    def __aiter__(self) -> AsyncIterator[str | bytes]: ...

    async def send(self, message: str) -> None: ...


class GameServer:
    """Own WebSocket lifecycle and compose focused multiplayer components."""

    _SIMULATION_INTERVAL_SECONDS = 0.016

    def __init__(
        self,
        game_engine: GameEngine,
        session_manager: SessionManager | None = None,
        command_parser: CommandParser | None = None,
        snapshot_serializer: GameSnapshotSerializer | None = None,
        event_serializer: GameEventSerializer | None = None,
        logger: logging.Logger | None = None,
        authentication_service: AuthenticationService | None = None,
        rating_service: PersistentRatingService | None = None,
        matchmaking_service: MatchmakingService | None = None,
        reconnect_service: ReconnectSessionService | None = None,
        room_service: PrivateRoomService | None = None,
        spectator_service: SpectatorService | None = None,
    ) -> None:
        self._game_engine = game_engine
        self._sessions = session_manager or SessionManager()
        self._command_parser = command_parser or CommandParser()
        self._snapshot_serializer = snapshot_serializer or GameSnapshotSerializer()
        self._event_serializer = event_serializer or GameEventSerializer()
        self._logger = logger or logging.getLogger(__name__)
        self._authentication_service = authentication_service
        self._rating_service = rating_service
        self._matchmaking = matchmaking_service or MatchmakingService()
        self._reconnect = reconnect_service or ReconnectSessionService()
        self._rooms = room_service or PrivateRoomService()
        self._spectators = spectator_service or SpectatorService()
        self._command_lock = asyncio.Lock()
        self._simulation_task: asyncio.Task[None] | None = None

        self._messenger = ClientMessenger(
            self._broadcast_recipients,
            self._logger,
        )
        self._authentication = AuthenticationHandler(
            authentication_service,
            self._messenger,
            self._logger,
        )
        self._authenticated_users = self._authentication.users
        self._game_commands = GameCommandHandler(game_engine, self._sessions)
        self._ratings = RatingFinalizer(
            rating_service,
            self._authentication,
            self._sessions,
            self._messenger,
            lambda: self._match_sessions.game_id,
            self._logger,
        )
        self._game_users_by_color = self._ratings.game_users_by_color
        self._spectator_handler = SpectatorHandler(
            self._spectators,
            self._matchmaking,
            self._rooms,
            self._reconnect,
            self._sessions,
            self._authentication,
            self._messenger,
            self._send_snapshot,
            self._ratings.profiles,
            self._logger,
        )
        self._match_sessions = MatchSessionCoordinator(
            self._sessions,
            self._matchmaking,
            self._rooms,
            self._spectator_handler,
            self._reconnect,
            self._authentication,
            self._messenger,
            self._ratings,
            self._send_snapshot,
            self._ratings.profiles,
            self._logger,
        )
        self._messenger.set_connection_failure_handler(
            self._match_sessions.disconnect
        )
        self._lobby = LobbyHandler(
            self._authentication,
            self._matchmaking,
            self._rooms,
            self._spectators,
            self._reconnect,
            self._sessions,
            self._messenger,
            self._start_match,
            self._logger,
        )
        self._message_router = ClientMessageRouter(
            self._authentication,
            self._lobby,
            self._spectator_handler,
            self._reconnect,
            self._match_sessions.resume,
            self._command_parser,
            self._game_commands,
            self._command_lock,
            self._messenger,
            self.broadcast_snapshot,
            self._logger,
        )
        self._runtime = GameRuntime(
            game_engine,
            self._snapshot_serializer,
            self._command_lock,
            self.broadcast,
            self._SIMULATION_INTERVAL_SECONDS,
        )
        self._events = GameEventPublisher(
            game_engine,
            self._event_serializer,
            self.broadcast,
            self._match_sessions.finish_game,
            lambda: self._match_sessions.game_id,
            self._logger,
        )

    @property
    def game_engine(self) -> GameEngine:
        """Return the single authoritative engine shared by all clients."""
        return self._game_engine

    async def handle_client(self, connection: ClientConnection) -> None:
        """Process one connection until it closes, then delegate cleanup."""
        self._events.set_loop(asyncio.get_running_loop())
        if self._authentication_service is None:
            if not await self._accept_game_client(connection):
                return
        else:
            self._log(logging.INFO, "client_connected")
        try:
            async for raw_message in connection:
                await self.handle_message(connection, raw_message)
        except ConnectionClosed:
            pass
        finally:
            color = self._sessions.color_for(connection)
            await self._handle_disconnect(connection)
            color_name = color.name.lower() if color is not None else "unassigned"
            self._log(logging.INFO, "client_disconnected", reason=color_name)

    async def handle_message(
        self,
        connection: ClientConnection,
        raw_message: str | bytes,
    ) -> None:
        """Delegate one external message to the focused message router."""
        await self._message_router.route(connection, raw_message)

    async def broadcast(self, message: dict[str, JsonValue]) -> None:
        """Broadcast one JSON-safe message to players and current spectators."""
        await self._messenger.broadcast(message)

    async def broadcast_snapshot(self) -> None:
        """Broadcast the current authoritative full game snapshot."""
        await self.broadcast(
            {
                "type": "game_snapshot",
                "state": self._snapshot_serializer.serialize(self._game_engine),
            }
        )

    async def run(self, host: str, port: int) -> None:
        """Serve WebSocket clients and the simulation until cancellation."""
        self._events.set_loop(asyncio.get_running_loop())
        self._simulation_task = asyncio.create_task(self._runtime.run())
        self._log(logging.INFO, "server_started", reason=f"{host}:{port}")
        try:
            async with serve(self.handle_client, host, port) as server:
                await server.serve_forever()
        finally:
            await self.close()
            self._log(logging.INFO, "server_stopped")

    async def close(self) -> None:
        """Stop background work and release component-owned lifecycle state."""
        simulation_task = self._simulation_task
        self._simulation_task = None
        if simulation_task is not None:
            simulation_task.cancel()
            await asyncio.gather(simulation_task, return_exceptions=True)
        await self._events.close()
        await self._match_sessions.close()

    def _broadcast_recipients(self) -> tuple[object, ...]:
        return (
            *self._sessions.clients,
            *self._spectator_handler.spectators_for(self._match_sessions.game_id),
        )

    async def _accept_game_client(self, connection: ClientConnection) -> bool:
        color = self._sessions.connect(connection)
        if color is None:
            self._logger.info("Rejected client connection: game is full")
            await self._messenger.send(
                connection, {"type": "connection_rejected", "reason": "game_full"}
            )
            return False
        self._logger.info("Client accepted with color %s", color.name)
        await self._messenger.send(
            connection, {"type": "connection_accepted", "color": color.name.lower()}
        )
        await self._send_snapshot(connection)
        return True

    async def _send_snapshot(self, connection: ClientConnection) -> None:
        await self._messenger.send(
            connection,
            {
                "type": "game_snapshot",
                "state": self._snapshot_serializer.serialize(self._game_engine),
            },
        )

    # Compatibility wrappers retained for existing integrations and tests.
    async def _start_match(self, match: Match) -> None:
        await self._match_sessions.start_match(match)

    async def _handle_disconnect(self, connection: object) -> None:
        await self._match_sessions.disconnect(connection)

    async def _close_spectator_views(self, game_id: str) -> None:
        await self._spectator_handler.close_game(game_id)

    async def _finalize_ratings(self, winner_color: PieceColor) -> None:
        await self._ratings.finalize(winner_color)

    def _log(self, level: int, event_type: str, **context: object) -> None:
        safe_context = {
            key: value for key, value in context.items() if value is not None
        }
        self._logger.log(
            level,
            event_type,
            extra={"event_type": event_type, **safe_context},
        )
