"""JSON decoding, access gates, and delegation for inbound client messages."""

import asyncio
import json
import logging
from collections.abc import Awaitable, Callable

from matchmaking.matchmaking_service import MatchmakingState
from network.server.authentication_handler import AuthenticationHandler
from network.server.transport.client_messenger import ClientMessenger, MessageConnection
from network.server.transport.command_parser import CommandParser
from network.server.transport.errors import CommandParseError
from network.server.matches.game_command_handler import GameCommandHandler
from network.server.lobby_handler import LobbyHandler
from network.server.matches.reconnect_session_service import ReconnectSessionService
from network.server.spectator_handler import SpectatorHandler


class ClientMessageRouter:
    """Routes decoded intent after high-level authentication and role checks."""

    def __init__(
        self,
        authentication: AuthenticationHandler,
        lobby: LobbyHandler,
        spectators: SpectatorHandler,
        reconnect: ReconnectSessionService,
        resume_session: Callable[[MessageConnection, object], Awaitable[None]],
        parser: CommandParser,
        game_commands: GameCommandHandler,
        command_lock: asyncio.Lock,
        messenger: ClientMessenger,
        broadcast_snapshot: Callable[[], Awaitable[None]],
        logger: logging.Logger,
    ) -> None:
        self._authentication = authentication
        self._lobby = lobby
        self._spectators = spectators
        self._reconnect = reconnect
        self._resume_session = resume_session
        self._parser = parser
        self._game_commands = game_commands
        self._command_lock = command_lock
        self._messenger = messenger
        self._broadcast_snapshot = broadcast_snapshot
        self._logger = logger

    async def route(
        self,
        connection: MessageConnection,
        raw_message: str | bytes,
    ) -> None:
        """Decode one message, enforce its access tier, and delegate it."""
        try:
            message = self.decode(raw_message)
        except json.JSONDecodeError:
            await self._messenger.reject(connection, "invalid_json")
            return
        except CommandParseError:
            await self._messenger.reject(connection, "malformed_command")
            return
        message_type = message.get("type")
        if self._authentication.service is not None and message_type == "resume_session":
            await self._resume_session(connection, message.get("token"))
            return
        if self._authentication.service is not None and message_type in {"register", "login"}:
            await self._authentication.handle(connection, message)
            return
        if (
            self._authentication.service is not None
            and connection not in self._authentication.users
        ):
            await self._messenger.reject(connection, "authentication_required")
            return
        room_routes = {
            "create_room": lambda: self._lobby.create_room(connection),
            "join_room": lambda: self._lobby.join_room(connection, message.get("room_code")),
            "cancel_room": lambda: self._lobby.cancel_room(connection),
        }
        spectator_routes = {
            "list_spectatable_games": lambda: self._spectators.list_games(connection),
            "spectate_game": lambda: self._spectators.start(
                connection, message.get("game_id")
            ),
            "stop_spectating": lambda: self._spectators.stop(connection),
        }
        if message_type in room_routes:
            await room_routes[str(message_type)]()
            return
        if message_type in spectator_routes:
            await spectator_routes[str(message_type)]()
            return
        if self._spectators.service.is_spectator(connection):
            await self._messenger.reject(connection, "spectator_read_only")
            return
        if self._authentication.service is not None and self._reconnect.is_paused():
            await self._messenger.send(
                connection, {"type": "game_paused", "reason": "opponent_disconnected"}
            )
            return
        if message_type == "start_matchmaking":
            await self._lobby.start_matchmaking(connection)
            return
        if message_type == "cancel_matchmaking":
            await self._lobby.cancel_matchmaking(connection)
            return
        if (
            self._authentication.service is not None
            and self._lobby.matchmaking.state_for(connection)
            is not MatchmakingState.IN_GAME
            and self._reconnect.participant_for_connection(connection) is None
        ):
            await self._messenger.reject(connection, "not_in_game")
            return
        await self._execute_game_command(connection, message)

    async def _execute_game_command(
        self,
        connection: MessageConnection,
        message: dict[str, object],
    ) -> None:
        try:
            command = self._parser.parse(message)
        except CommandParseError:
            await self._messenger.reject(connection, "malformed_command")
            return
        try:
            async with self._command_lock:
                response = self._game_commands.execute(connection, command)
        except Exception:
            self._logger.exception("Unexpected server error while executing command")
            await self._messenger.send(connection, {"type": "server_error"})
            return
        await self._messenger.send(connection, response)
        if response["type"] == "command_accepted":
            await self._broadcast_snapshot()

    @staticmethod
    def decode(raw_message: str | bytes) -> dict[str, object]:
        decoded = json.loads(raw_message)
        if not isinstance(decoded, dict):
            raise CommandParseError("Command JSON must contain an object.")
        return decoded
