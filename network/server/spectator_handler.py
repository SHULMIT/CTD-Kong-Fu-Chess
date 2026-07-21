"""Read-only active-game discovery and spectator transport workflow."""

import logging
from collections.abc import Awaitable, Callable

from matchmaking.matchmaking_service import MatchmakingService, MatchmakingState
from network.server.authentication_handler import AuthenticationHandler
from network.server.transport.client_messenger import ClientMessenger, MessageConnection
from network.server.transport.game_snapshot_serializer import JsonValue
from network.server.matches.reconnect_session_service import ReconnectSessionService
from network.server.matches.session_manager import SessionManager
from rooms.private_room_service import PrivateRoomService
from spectators.spectator_service import SpectatableGame, SpectatorService


class SpectatorHandler:
    """Lists games and manages read-only viewer membership and notifications."""

    def __init__(
        self,
        spectators: SpectatorService,
        matchmaking: MatchmakingService,
        rooms: PrivateRoomService,
        reconnect: ReconnectSessionService,
        sessions: SessionManager,
        authentication: AuthenticationHandler,
        messenger: ClientMessenger,
        send_snapshot: Callable[[MessageConnection], Awaitable[None]],
        profile_provider: Callable[[], list[JsonValue]],
        logger: logging.Logger,
    ) -> None:
        self.service = spectators
        self._matchmaking = matchmaking
        self._rooms = rooms
        self._reconnect = reconnect
        self._sessions = sessions
        self._authentication = authentication
        self._messenger = messenger
        self._send_snapshot = send_snapshot
        self._profile_provider = profile_provider
        self._logger = logger

    async def list_games(self, connection: MessageConnection) -> None:
        games: list[JsonValue] = []
        for game in self.service.list_games():
            games.append(
                {
                    "game_id": game.game_id,
                    "white": {"username": game.white.username, "rating": game.white.rating},
                    "black": {"username": game.black.username, "rating": game.black.rating},
                }
            )
        await self._messenger.send(
            connection, {"type": "spectatable_games", "games": games}
        )

    def register_game(self, game: SpectatableGame) -> None:
        """Register one authoritative game for discovery."""
        self.service.register_game(game)

    def leave(self, connection: object) -> str | None:
        """Remove a spectator connection and return its former game ID."""
        return self.service.leave(connection)

    def spectators_for(self, game_id: str) -> tuple[object, ...]:
        """Return the current viewers for one game."""
        return self.service.spectators_for(game_id)

    async def start(self, connection: MessageConnection, game_id: object) -> None:
        if not self._can_start(connection):
            await self._error(connection, "invalid_state")
            return
        if not self.service.join(game_id, connection):
            await self._error(connection, "game_not_found")
            return
        await self._messenger.send(
            connection, {"type": "spectating_started", "game_id": str(game_id)}
        )
        user = self._authentication.lookup(connection)
        self._log(
            "spectator_joined",
            game_id=str(game_id),
            user_id=user.id if user else None,
            username=user.username if user else None,
        )
        await self._send_snapshot(connection)
        await self._messenger.send(
            connection, {"type": "player_profiles", "players": self._profile_provider()}
        )

    async def stop(self, connection: MessageConnection) -> None:
        game_id = self.service.leave(connection)
        if game_id is None:
            await self._error(connection, "invalid_state")
            return
        await self._messenger.send(connection, {"type": "spectating_stopped"})
        self._log("spectator_left", game_id=game_id)

    async def close_game(self, game_id: str) -> None:
        for spectator in self.service.close_game(game_id):
            await self._messenger.send(
                spectator, {"type": "spectating_stopped", "reason": "game_ended"}
            )

    def _can_start(self, connection: object) -> bool:
        return (
            self._matchmaking.state_for(connection) is MatchmakingState.IDLE
            and not self._rooms.contains(connection)
            and self._reconnect.participant_for_connection(connection) is None
            and self._sessions.color_for(connection) is None
            and not self.service.is_spectator(connection)
        )

    async def _error(self, connection: MessageConnection, reason: str) -> None:
        await self._messenger.send(
            connection, {"type": "spectator_error", "reason": reason}
        )

    def _log(self, event_type: str, **context: object) -> None:
        safe = {key: value for key, value in context.items() if value is not None}
        self._logger.info(event_type, extra={"event_type": event_type, **safe})
