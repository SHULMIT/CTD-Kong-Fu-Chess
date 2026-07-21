"""Matched-player ownership, reconnect lifecycle, and session cleanup."""

import asyncio
from datetime import datetime, timezone
import logging
from collections.abc import Awaitable, Callable
from uuid import uuid4

from matchmaking.matchmaking_service import Match, MatchmakingService
from model.piece import PieceColor
from network.server.authentication_handler import AuthenticationHandler
from network.server.transport.client_messenger import ClientMessenger, MessageConnection
from network.server.transport.game_snapshot_serializer import JsonValue
from network.server.matches.rating_finalizer import RatingFinalizer
from network.server.matches.reconnect_session_service import DisconnectNotice, ReconnectSessionService
from network.server.matches.session_manager import SessionManager
from network.server.spectator_handler import SpectatorHandler
from rooms.private_room_service import PrivateRoomService
from spectators.spectator_service import SpectatableGame


class MatchSessionCoordinator:
    """Owns one active match's players, resume timers, and terminal cleanup."""

    def __init__(
        self,
        sessions: SessionManager,
        matchmaking: MatchmakingService,
        rooms: PrivateRoomService,
        spectator_handler: SpectatorHandler,
        reconnect: ReconnectSessionService,
        authentication: AuthenticationHandler,
        messenger: ClientMessenger,
        rating_finalizer: RatingFinalizer,
        send_snapshot: Callable[[MessageConnection], Awaitable[None]],
        profile_provider: Callable[[], list[JsonValue]],
        logger: logging.Logger,
    ) -> None:
        self._sessions = sessions
        self._matchmaking = matchmaking
        self._rooms = rooms
        self._spectator_handler = spectator_handler
        self._reconnect = reconnect
        self._authentication = authentication
        self._messenger = messenger
        self._ratings = rating_finalizer
        self._send_snapshot = send_snapshot
        self._profile_provider = profile_provider
        self._logger = logger
        self._disconnect_tasks: dict[int, asyncio.Task[None]] = {}
        self.game_id = str(uuid4())

    async def start_match(self, match: Match) -> None:
        """Assign colors and continue the existing authoritative start flow."""
        if self._sessions.clients:
            self._matchmaking.disconnect(match.white.client)
            self._matchmaking.disconnect(match.black.client)
            await self._messenger.send(match.white.client, {"type": "server_error"})
            await self._messenger.send(match.black.client, {"type": "server_error"})
            return
        self._sessions.assign(match.white.client, PieceColor.WHITE)
        self._sessions.assign(match.black.client, PieceColor.BLACK)
        self.game_id = match.game_id
        self._ratings.set_players(match.white.user, match.black.user)
        tokens = self._reconnect.create_game(
            match.game_id,
            (
                (match.white.client, match.white.user, PieceColor.WHITE),
                (match.black.client, match.black.user, PieceColor.BLACK),
            ),
        )
        self._spectator_handler.register_game(
            SpectatableGame(match.game_id, match.white.user, match.black.user)
        )
        self._log("game_started", game_id=match.game_id)
        self._log("match_created", game_id=match.game_id)
        match_message: dict[str, JsonValue] = {
            "type": "match_found",
            "game_id": match.game_id,
            "players": self._profile_provider(),
        }
        for connection, color in (
            (match.white.client, PieceColor.WHITE),
            (match.black.client, PieceColor.BLACK),
        ):
            await self._messenger.send(connection, match_message)
            await self._messenger.send(
                connection, {"type": "connection_accepted", "color": color.name.lower()}
            )
            await self._send_snapshot(connection)
            await self._messenger.send(
                connection, {"type": "session_resume_token", "token": tokens[connection]}
            )
            self._matchmaking.mark_in_game(connection)

    async def disconnect(self, connection: object) -> None:
        """Clean waiting clients or begin the active-player resume window."""
        spectator_game = self._spectator_handler.leave(connection)
        if spectator_game is not None:
            self._log("spectator_left", game_id=spectator_game)
            self._authentication.remove(connection)
            return
        closed_room = self._rooms.disconnect(connection)
        if closed_room is not None:
            self._log("room_cleaned_up", room_code=closed_room)
        self._matchmaking.disconnect(connection)
        notice = self._reconnect.disconnect(connection)
        self._sessions.disconnect(connection)
        self._authentication.remove(connection)
        if notice is None:
            return
        self._log(
            "participant_disconnected",
            logging.WARNING,
            game_id=notice.game_id,
            user_id=notice.user.id,
            username=notice.user.username,
        )
        if notice.opponent_connection is not None:
            await self._messenger.send(
                notice.opponent_connection,
                {
                    "type": "opponent_disconnected",
                    "game_id": notice.game_id,
                    "username": notice.user.username,
                    "reconnect_timeout_seconds": self._reconnect.timeout_seconds,
                    "deadline": datetime.fromtimestamp(
                        notice.deadline, timezone.utc
                    ).isoformat(),
                },
            )
        await self._cancel_disconnect_task(notice.user.id)
        self._disconnect_tasks[notice.user.id] = asyncio.create_task(
            self._wait_for_timeout(notice)
        )

    async def resume(self, connection: MessageConnection, token: object) -> None:
        """Attach a validated replacement connection to the existing match."""
        result = self._reconnect.resume(connection, token)
        if result is None:
            await self._messenger.send(
                connection,
                {"type": "session_resume_rejected", "reason": "invalid_or_expired_token"},
            )
            return
        await self._cancel_disconnect_task(result.user.id)
        self._authentication.attach(connection, result.user)
        self._sessions.assign(connection, result.color)
        self._log(
            "session_resumed",
            game_id=result.game_id,
            user_id=result.user.id,
            username=result.user.username,
        )
        await self._messenger.send(
            connection,
            {
                "type": "session_resumed",
                "game_id": result.game_id,
                "color": result.color.name.lower(),
            },
        )
        await self._messenger.send(
            connection, {"type": "session_resume_token", "token": result.token}
        )
        await self._send_snapshot(connection)
        await self._messenger.send(
            connection, {"type": "player_profiles", "players": self._profile_provider()}
        )
        if result.opponent_connection is not None:
            await self._messenger.send(
                result.opponent_connection,
                {
                    "type": "opponent_reconnected",
                    "game_id": result.game_id,
                    "username": result.user.username,
                },
            )

    async def finish_game(self, winner: PieceColor | None) -> None:
        """Finalize ratings and close all read-only views for this game."""
        await self._cancel_all_disconnect_tasks()
        if winner is not None:
            await self._ratings.finalize(winner)
        self._reconnect.cleanup()
        await self._spectator_handler.close_game(self.game_id)

    async def close(self) -> None:
        """Cancel owned timeout work and release reconnect session state."""
        await self._cancel_all_disconnect_tasks()
        self._reconnect.cleanup()

    async def _wait_for_timeout(self, notice: DisconnectNotice) -> None:
        try:
            delay = max(0.0, notice.deadline - datetime.now(timezone.utc).timestamp())
            await asyncio.sleep(delay)
            result = self._reconnect.expire(notice.user.id, notice.deadline)
            if result is None:
                return
            self._log(
                "reconnect_timeout",
                logging.WARNING,
                game_id=result.game_id,
                user_id=notice.user.id,
                username=notice.user.username,
            )
            if result.winner_color is not None:
                await self._ratings.finalize(result.winner_color)
            message: dict[str, JsonValue] = {
                "type": "disconnect_forfeit",
                "game_id": result.game_id,
                "winner": result.winner.username if result.winner else None,
                "loser": result.loser.username if result.loser else None,
                "reason": "reconnect_timeout",
            }
            for target in result.connections:
                await self._messenger.send(target, message)
            self._log(
                "disconnect_forfeit",
                logging.WARNING,
                game_id=result.game_id,
                username=result.loser.username if result.loser else None,
            )
            for target in result.connections:
                self._sessions.disconnect(target)
                self._matchmaking.disconnect(target)
                self._authentication.remove(target)
            self._reconnect.cleanup()
            await self._spectator_handler.close_game(result.game_id)
            self._ratings.clear()
        except asyncio.CancelledError:
            return
        finally:
            current = asyncio.current_task()
            if self._disconnect_tasks.get(notice.user.id) is current:
                self._disconnect_tasks.pop(notice.user.id, None)

    async def _cancel_disconnect_task(self, user_id: int) -> None:
        task = self._disconnect_tasks.pop(user_id, None)
        if task is None or task is asyncio.current_task():
            return
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)

    async def _cancel_all_disconnect_tasks(self) -> None:
        current = asyncio.current_task()
        tasks = tuple(
            task for task in self._disconnect_tasks.values() if task is not current
        )
        self._disconnect_tasks.clear()
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    def _log(
        self,
        event_type: str,
        level: int = logging.INFO,
        **context: object,
    ) -> None:
        safe = {key: value for key, value in context.items() if value is not None}
        self._logger.log(level, event_type, extra={"event_type": event_type, **safe})
