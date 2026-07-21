"""Authenticated matchmaking and private-room WebSocket workflows."""

import asyncio
import logging
from collections.abc import Awaitable, Callable

from matchmaking.matchmaking_service import (
    Match,
    MatchmakingEntry,
    MatchmakingService,
    MatchmakingState,
)
from network.server.authentication_handler import AuthenticationHandler
from network.server.transport.client_messenger import ClientMessenger, MessageConnection
from network.server.transport.game_snapshot_serializer import JsonValue
from network.server.matches.reconnect_session_service import ReconnectSessionService
from network.server.matches.session_manager import SessionManager
from rooms.private_room_service import PrivateRoomError, PrivateRoomService
from spectators.spectator_service import SpectatorService


class LobbyHandler:
    """Coordinates waiting-state actions and requests match creation."""

    def __init__(
        self,
        authentication: AuthenticationHandler,
        matchmaking: MatchmakingService,
        rooms: PrivateRoomService,
        spectators: SpectatorService,
        reconnect: ReconnectSessionService,
        sessions: SessionManager,
        messenger: ClientMessenger,
        start_match: Callable[[Match], Awaitable[None]],
        logger: logging.Logger,
    ) -> None:
        self._authentication = authentication
        self.matchmaking = matchmaking
        self.rooms = rooms
        self._spectators = spectators
        self._reconnect = reconnect
        self._sessions = sessions
        self._messenger = messenger
        self._start_match = start_match
        self._logger = logger

    async def start_matchmaking(self, connection: MessageConnection) -> None:
        if self.rooms.contains(connection) or self._spectators.is_spectator(connection):
            await self._messenger.reject(connection, "invalid_state")
            return
        current = await self._authentication.refresh(connection)
        if current is None:
            await self._messenger.send(connection, {"type": "server_error"})
            return
        previous = self.matchmaking.state_for(connection)
        match = self.matchmaking.enqueue(connection, current)
        if match is not None:
            await self._start_match(match)
            return
        if previous is MatchmakingState.IDLE:
            self._log("matchmaking_joined", user_id=current.id, username=current.username)
            await self._messenger.send(
                connection, {"type": "matchmaking_queued", "rating": current.rating}
            )
            return
        await self._messenger.send(
            connection, {"type": "matchmaking_status", "state": previous.value}
        )

    async def cancel_matchmaking(self, connection: MessageConnection) -> None:
        if self.matchmaking.cancel(connection):
            user = self._authentication.lookup(connection)
            self._log(
                "matchmaking_canceled",
                user_id=user.id if user else None,
                username=user.username if user else None,
            )
            await self._messenger.send(connection, {"type": "matchmaking_canceled"})
            return
        await self._messenger.reject(connection, "not_searching")

    async def create_room(self, connection: MessageConnection) -> None:
        if not self._can_create_room(connection):
            await self._room_error(connection, "invalid_state")
            return
        user = await self._authentication.refresh(connection)
        if user is None:
            await self._messenger.send(connection, {"type": "server_error"})
            return
        try:
            room = self.rooms.create(connection, user)
        except PrivateRoomError as error:
            await self._room_error(connection, error.code.value)
            return
        await self._messenger.send(
            connection, {"type": "room_created", "room_code": room.code}
        )
        self._log("room_created", room_code=room.code, user_id=user.id, username=user.username)

    async def join_room(
        self,
        connection: MessageConnection,
        room_code: object,
    ) -> None:
        if not self._can_join_room(connection):
            await self._room_error(connection, "invalid_state")
            return
        user = await self._authentication.refresh(connection)
        if user is None:
            await self._messenger.send(connection, {"type": "server_error"})
            return
        try:
            room_match = self.rooms.join(room_code, connection, user)
        except PrivateRoomError as error:
            await self._room_error(connection, error.code.value)
            return
        creator = room_match.creator
        service = self._authentication.service
        if service is not None:
            current_creator = await asyncio.to_thread(
                service.current_user, creator.username
            )
            if current_creator is not None:
                creator = current_creator
                self._authentication.attach(room_match.creator_connection, creator)
        joined: dict[str, JsonValue] = {
            "type": "room_joined",
            "room_code": room_match.room_code,
        }
        await self._messenger.send(connection, joined)
        await self._messenger.send(room_match.creator_connection, joined)
        self._log(
            "room_joined",
            room_code=room_match.room_code,
            game_id=room_match.game_id,
            user_id=user.id,
            username=user.username,
        )
        await self._start_match(
            Match(
                room_match.game_id,
                MatchmakingEntry(room_match.creator_connection, creator),
                MatchmakingEntry(room_match.guest_connection, user),
            )
        )
        self.rooms.release_match(room_match.room_code)

    async def cancel_room(self, connection: MessageConnection) -> None:
        try:
            room_code = self.rooms.cancel(connection)
        except PrivateRoomError as error:
            await self._room_error(connection, error.code.value)
            return
        await self._messenger.send(
            connection, {"type": "room_closed", "room_code": room_code}
        )
        self._log("room_canceled", room_code=room_code)

    def _can_create_room(self, connection: object) -> bool:
        return self._can_join_room(connection) and not self._sessions.clients

    def _can_join_room(self, connection: object) -> bool:
        return (
            self.matchmaking.state_for(connection) is MatchmakingState.IDLE
            and not self.rooms.contains(connection)
            and self._reconnect.participant_for_connection(connection) is None
        )

    async def _room_error(self, connection: MessageConnection, reason: str) -> None:
        await self._messenger.send(connection, {"type": "room_error", "reason": reason})

    def _log(self, event_type: str, **context: object) -> None:
        safe = {key: value for key, value in context.items() if value is not None}
        self._logger.info(event_type, extra={"event_type": event_type, **safe})
