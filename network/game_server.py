"""Async WebSocket orchestration for one authoritative local game."""

import asyncio
from collections.abc import AsyncIterator
import json
import logging
from datetime import datetime, timezone
from typing import Protocol, cast
from uuid import uuid4

from authentication.authentication_service import AuthenticationService
from authentication.errors import (
    AuthenticationValidationError,
    InvalidCredentialsError,
    UsernameTakenError,
)
from authentication.user import User
from errors.user_input_errors import UserInputError
from events.event import Event
from events.game_events import (
    GameOverEvent,
    JumpCompletedEvent,
    JumpStartedEvent,
    MoveCompletedEvent,
    MoveStartedEvent,
    ScoreChangedEvent,
)
from game.game_engine import GameEngine
from matchmaking.matchmaking_service import (
    Match,
    MatchmakingEntry,
    MatchmakingService,
    MatchmakingState,
)
from model.piece import Piece, PieceColor
from model.position import Position
from network.command_parser import CommandParser
from network.commands import (
    JumpCommand,
    LegalMovesCommand,
    MoveCommand,
    NetworkCommand,
)
from network.errors import CommandParseError
from network.game_event_serializer import GameEventSerializer
from network.game_snapshot_serializer import GameSnapshotSerializer, JsonValue
from network.session_manager import SessionManager
from network.reconnect_session_service import (
    DisconnectNotice,
    ReconnectSessionService,
)
from rating.persistent_rating_service import PersistentRatingService, RatingUpdate
from rooms.private_room_service import PrivateRoomError, PrivateRoomService
from spectators.spectator_service import SpectatableGame, SpectatorService
from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosed


class ClientConnection(Protocol):
    """Minimum async connection behavior required by ``GameServer``."""

    def __aiter__(self) -> AsyncIterator[str | bytes]: ...

    async def send(self, message: str) -> None: ...


class GameServer:
    """Coordinates clients and commands for one authoritative game engine."""

    _SIMULATION_INTERVAL_SECONDS = 0.016
    _OBSERVED_EVENT_TYPES = (
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
        self._snapshot_serializer = (
            snapshot_serializer or GameSnapshotSerializer()
        )
        self._event_serializer = event_serializer or GameEventSerializer()
        self._logger = logger or logging.getLogger(__name__)
        self._authentication_service = authentication_service
        self._authenticated_users: dict[object, User] = {}
        self._rating_service = rating_service
        self._matchmaking = matchmaking_service or MatchmakingService()
        self._reconnect = reconnect_service or ReconnectSessionService()
        self._rooms = room_service or PrivateRoomService()
        self._spectators = spectator_service or SpectatorService()
        self._disconnect_tasks: dict[int, asyncio.Task[None]] = {}
        self._game_users_by_color: dict[PieceColor, User] = {}
        self._game_id = str(uuid4())
        self._rating_finalization_started = False
        self._command_lock = asyncio.Lock()
        self._loop: asyncio.AbstractEventLoop | None = None
        self._broadcast_tasks: set[asyncio.Task[None]] = set()
        self._next_event_id = 1
        self._subscribe_to_game_events()

    @property
    def game_engine(self) -> GameEngine:
        """Return the single authoritative engine shared by all clients."""
        return self._game_engine

    async def handle_client(self, connection: ClientConnection) -> None:
        """Accept one connection and process messages until it disconnects."""
        self._loop = asyncio.get_running_loop()
        if self._authentication_service is None:
            accepted = await self._accept_game_client(connection)
            if not accepted:
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
            color_name = color.name if color is not None else "UNASSIGNED"
            self._log(logging.INFO, "client_disconnected", reason=color_name.lower())

    async def handle_message(
        self,
        connection: ClientConnection,
        raw_message: str | bytes,
    ) -> None:
        """Decode, authorize, and execute one external client message."""
        try:
            message = self._decode_message(raw_message)
        except json.JSONDecodeError:
            await self._reject(connection, "invalid_json")
            return
        except CommandParseError:
            await self._reject(connection, "malformed_command")
            return

        message_type = message.get("type")
        if self._authentication_service is not None and message_type == "resume_session":
            await self._handle_session_resume(connection, message.get("token"))
            return
        if self._authentication_service is not None and message_type in {
            "register",
            "login",
        }:
            await self._handle_authentication(connection, message)
            return
        if (
            self._authentication_service is not None
            and connection not in self._authenticated_users
        ):
            await self._reject(connection, "authentication_required")
            return
        if self._authentication_service is not None and message_type == "create_room":
            await self._handle_create_room(connection)
            return
        if self._authentication_service is not None and message_type == "join_room":
            await self._handle_join_room(connection, message.get("room_code"))
            return
        if self._authentication_service is not None and message_type == "cancel_room":
            await self._handle_cancel_room(connection)
            return
        if message_type == "list_spectatable_games":
            await self._handle_list_spectatable_games(connection)
            return
        if message_type == "spectate_game":
            await self._handle_spectate_game(connection, message.get("game_id"))
            return
        if message_type == "stop_spectating":
            await self._handle_stop_spectating(connection)
            return
        if self._spectators.is_spectator(connection):
            await self._reject(connection, "spectator_read_only")
            return
        if self._authentication_service is not None and self._reconnect.is_paused():
            await self._send_message(
                connection,
                {"type": "game_paused", "reason": "opponent_disconnected"},
            )
            return
        if self._authentication_service is not None and message_type == "start_matchmaking":
            await self._handle_matchmaking_request(connection)
            return
        if self._authentication_service is not None and message_type == "cancel_matchmaking":
            await self._handle_matchmaking_cancel(connection)
            return
        if (
            self._authentication_service is not None
            and self._matchmaking.state_for(connection) is not MatchmakingState.IN_GAME
            and self._reconnect.participant_for_connection(connection) is None
        ):
            await self._reject(connection, "not_in_game")
            return

        try:
            command = self._command_parser.parse(message)
        except CommandParseError:
            await self._reject(connection, "malformed_command")
            return

        try:
            async with self._command_lock:
                response = self._execute_command(connection, command)
        except Exception:
            self._logger.exception("Unexpected server error while executing command")
            await self._send_message(connection, {"type": "server_error"})
            return

        await self._send_message(connection, response)
        if response["type"] == "command_accepted":
            await self.broadcast_snapshot()

    async def _handle_authentication(
        self,
        connection: ClientConnection,
        message: dict[str, object],
    ) -> None:
        service = self._authentication_service
        if service is None:
            return
        username = message.get("username")
        password = message.get("password")
        try:
            if message["type"] == "register":
                user = await asyncio.to_thread(
                    service.register,
                    username,
                    password,
                )
                await self._send_message(
                    connection,
                    self._authentication_response("registration_success", user),
                )
                self._log(
                    logging.INFO,
                    "registration_succeeded",
                    user_id=user.id,
                    username=user.username,
                )
                return

            user = await asyncio.to_thread(service.login, username, password)
            self._authenticated_users[connection] = user
            await self._send_message(
                connection,
                self._authentication_response("login_success", user),
            )
            self._log(
                logging.INFO,
                "login_succeeded",
                user_id=user.id,
                username=user.username,
            )
        except UsernameTakenError:
            self._log(logging.WARNING, "registration_failed", reason="username_taken")
            await self._send_message(connection, {"type": "username_taken"})
        except InvalidCredentialsError:
            self._log(logging.WARNING, "login_failed", reason="invalid_credentials")
            await self._send_message(connection, {"type": "invalid_credentials"})
        except AuthenticationValidationError:
            self._log(logging.WARNING, "authentication_validation_failed")
            await self._send_message(connection, {"type": "validation_error"})
        except Exception:
            self._logger.exception("Unexpected authentication server error")
            await self._send_message(connection, {"type": "server_error"})

    async def _handle_matchmaking_request(
        self,
        connection: ClientConnection,
    ) -> None:
        service = self._authentication_service
        authenticated_user = self._authenticated_users[connection]
        if service is None:
            return
        if self._rooms.contains(connection):
            await self._reject(connection, "invalid_state")
            return
        if self._spectators.is_spectator(connection):
            await self._reject(connection, "invalid_state")
            return
        current_user = await asyncio.to_thread(
            service.current_user,
            authenticated_user.username,
        )
        if current_user is None:
            await self._send_message(connection, {"type": "server_error"})
            return
        self._authenticated_users[connection] = current_user
        previous_state = self._matchmaking.state_for(connection)
        match = self._matchmaking.enqueue(connection, current_user)
        if match is not None:
            await self._start_match(match)
            return
        if previous_state is MatchmakingState.IDLE:
            self._log(
                logging.INFO,
                "matchmaking_joined",
                user_id=current_user.id,
                username=current_user.username,
            )
            await self._send_message(
                connection,
                {"type": "matchmaking_queued", "rating": current_user.rating},
            )
            return
        await self._send_message(
            connection,
            {"type": "matchmaking_status", "state": previous_state.value},
        )

    async def _handle_matchmaking_cancel(
        self,
        connection: ClientConnection,
    ) -> None:
        if self._matchmaking.cancel(connection):
            user = self._authenticated_users.get(connection)
            self._log(
                logging.INFO,
                "matchmaking_canceled",
                user_id=user.id if user else None,
                username=user.username if user else None,
            )
            await self._send_message(connection, {"type": "matchmaking_canceled"})
            return
        await self._reject(connection, "not_searching")

    async def _handle_create_room(self, connection: ClientConnection) -> None:
        if not self._can_enter_private_room(connection):
            await self._send_room_error(connection, "invalid_state")
            return
        service = self._authentication_service
        user = self._authenticated_users[connection]
        if service is not None:
            current = await asyncio.to_thread(service.current_user, user.username)
            if current is not None:
                user = current
                self._authenticated_users[connection] = current
        try:
            room = self._rooms.create(connection, user)
        except PrivateRoomError as error:
            await self._send_room_error(connection, error.code.value)
            return
        await self._send_message(
            connection,
            {"type": "room_created", "room_code": room.code},
        )
        self._log(
            logging.INFO,
            "room_created",
            room_code=room.code,
            user_id=user.id,
            username=user.username,
        )

    async def _handle_join_room(
        self,
        connection: ClientConnection,
        room_code: object,
    ) -> None:
        if not self._can_join_private_room(connection):
            await self._send_room_error(connection, "invalid_state")
            return
        user = self._authenticated_users[connection]
        service = self._authentication_service
        if service is not None:
            current = await asyncio.to_thread(service.current_user, user.username)
            if current is not None:
                user = current
                self._authenticated_users[connection] = current
        try:
            room_match = self._rooms.join(room_code, connection, user)
        except PrivateRoomError as error:
            await self._send_room_error(connection, error.code.value)
            return
        creator = room_match.creator
        if service is not None:
            current_creator = await asyncio.to_thread(
                service.current_user, creator.username
            )
            if current_creator is not None:
                creator = current_creator
                self._authenticated_users[room_match.creator_connection] = creator
        room_joined: dict[str, JsonValue] = {
            "type": "room_joined",
            "room_code": room_match.room_code,
        }
        await self._send_message(connection, room_joined)
        await self._send_message(
            cast(ClientConnection, room_match.creator_connection), room_joined
        )
        self._log(
            logging.INFO,
            "room_joined",
            room_code=room_match.room_code,
            user_id=user.id,
            username=user.username,
            game_id=room_match.game_id,
        )
        match = Match(
            room_match.game_id,
            MatchmakingEntry(room_match.creator_connection, creator),
            MatchmakingEntry(room_match.guest_connection, user),
        )
        await self._start_match(match)
        self._rooms.release_match(room_match.room_code)

    async def _handle_cancel_room(self, connection: ClientConnection) -> None:
        try:
            room_code = self._rooms.cancel(connection)
        except PrivateRoomError as error:
            await self._send_room_error(connection, error.code.value)
            return
        await self._send_message(
            connection,
            {"type": "room_closed", "room_code": room_code},
        )
        self._log(logging.INFO, "room_canceled", room_code=room_code)

    def _can_enter_private_room(self, connection: object) -> bool:
        return (
            self._matchmaking.state_for(connection) is MatchmakingState.IDLE
            and not self._rooms.contains(connection)
            and self._reconnect.participant_for_connection(connection) is None
            and not self._sessions.clients
        )

    def _can_join_private_room(self, connection: object) -> bool:
        return (
            self._matchmaking.state_for(connection) is MatchmakingState.IDLE
            and not self._rooms.contains(connection)
            and self._reconnect.participant_for_connection(connection) is None
        )

    async def _send_room_error(
        self,
        connection: ClientConnection,
        reason: str,
    ) -> None:
        await self._send_message(
            connection,
            {"type": "room_error", "reason": reason},
        )

    async def _handle_list_spectatable_games(
        self,
        connection: ClientConnection,
    ) -> None:
        games: list[JsonValue] = []
        for game in self._spectators.list_games():
            games.append(
                {
                    "game_id": game.game_id,
                    "white": {
                        "username": game.white.username,
                        "rating": game.white.rating,
                    },
                    "black": {
                        "username": game.black.username,
                        "rating": game.black.rating,
                    },
                }
            )
        await self._send_message(
            connection,
            {"type": "spectatable_games", "games": games},
        )

    async def _handle_spectate_game(
        self,
        connection: ClientConnection,
        game_id: object,
    ) -> None:
        if not self._can_start_spectating(connection):
            await self._send_spectator_error(connection, "invalid_state")
            return
        if not self._spectators.join(game_id, connection):
            await self._send_spectator_error(connection, "game_not_found")
            return
        await self._send_message(
            connection,
            {"type": "spectating_started", "game_id": str(game_id)},
        )
        user = self._authenticated_users.get(connection)
        self._log(
            logging.INFO,
            "spectator_joined",
            game_id=str(game_id),
            user_id=user.id if user else None,
            username=user.username if user else None,
        )
        await self._send_snapshot(connection)
        await self._send_message(
            connection,
            {"type": "player_profiles", "players": self._profile_payloads()},
        )

    async def _handle_stop_spectating(self, connection: ClientConnection) -> None:
        game_id = self._spectators.leave(connection)
        if game_id is None:
            await self._send_spectator_error(connection, "invalid_state")
            return
        await self._send_message(connection, {"type": "spectating_stopped"})
        self._log(logging.INFO, "spectator_left", game_id=game_id)

    def _can_start_spectating(self, connection: object) -> bool:
        return (
            self._matchmaking.state_for(connection) is MatchmakingState.IDLE
            and not self._rooms.contains(connection)
            and self._reconnect.participant_for_connection(connection) is None
            and self._sessions.color_for(connection) is None
            and not self._spectators.is_spectator(connection)
        )

    async def _send_spectator_error(
        self,
        connection: ClientConnection,
        reason: str,
    ) -> None:
        await self._send_message(
            connection,
            {"type": "spectator_error", "reason": reason},
        )

    async def _start_match(self, match: Match) -> None:
        if self._sessions.clients:
            self._matchmaking.disconnect(match.white.client)
            self._matchmaking.disconnect(match.black.client)
            await self._send_message(match.white.client, {"type": "server_error"})
            await self._send_message(match.black.client, {"type": "server_error"})
            return
        self._sessions.assign(match.white.client, PieceColor.WHITE)
        self._sessions.assign(match.black.client, PieceColor.BLACK)
        self._game_id = match.game_id
        self._rating_finalization_started = False
        self._game_users_by_color = {
            PieceColor.WHITE: match.white.user,
            PieceColor.BLACK: match.black.user,
        }
        resume_tokens = self._reconnect.create_game(
            match.game_id,
            (
                (match.white.client, match.white.user, PieceColor.WHITE),
                (match.black.client, match.black.user, PieceColor.BLACK),
            ),
        )
        self._spectators.register_game(
            SpectatableGame(match.game_id, match.white.user, match.black.user)
        )
        self._log(
            logging.INFO,
            "game_started",
            game_id=match.game_id,
        )
        self._log(
            logging.INFO,
            "match_created",
            game_id=match.game_id,
        )
        profiles = self._profile_payloads()
        match_message: dict[str, JsonValue] = {
            "type": "match_found",
            "game_id": match.game_id,
            "players": profiles,
        }
        for connection, color in (
            (match.white.client, PieceColor.WHITE),
            (match.black.client, PieceColor.BLACK),
        ):
            client = cast(ClientConnection, connection)
            await self._send_message(client, match_message)
            await self._send_message(
                client,
                {"type": "connection_accepted", "color": color.name.lower()},
            )
            await self._send_snapshot(client)
            await self._send_message(
                client,
                {"type": "session_resume_token", "token": resume_tokens[connection]},
            )
            self._matchmaking.mark_in_game(connection)

    async def _handle_disconnect(self, connection: object) -> None:
        spectator_game_id = self._spectators.leave(connection)
        if spectator_game_id is not None:
            self._log(logging.INFO, "spectator_left", game_id=spectator_game_id)
            self._authenticated_users.pop(connection, None)
            return
        closed_room = self._rooms.disconnect(connection)
        if closed_room is not None:
            self._log(logging.INFO, "room_cleaned_up", room_code=closed_room)
        self._matchmaking.disconnect(connection)
        notice = self._reconnect.disconnect(connection)
        self._sessions.disconnect(connection)
        self._authenticated_users.pop(connection, None)
        if notice is None:
            return
        self._log(
            logging.WARNING,
            "participant_disconnected",
            game_id=notice.game_id,
            user_id=notice.user.id,
            username=notice.user.username,
        )
        if notice.opponent_connection is not None:
            await self._send_message(
                cast(ClientConnection, notice.opponent_connection),
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
        old_task = self._disconnect_tasks.pop(notice.user.id, None)
        if old_task is not None:
            old_task.cancel()
        task = asyncio.create_task(self._wait_for_disconnect_timeout(notice))
        self._disconnect_tasks[notice.user.id] = task

    async def _handle_session_resume(
        self,
        connection: ClientConnection,
        token: object,
    ) -> None:
        result = self._reconnect.resume(connection, token)
        if result is None:
            await self._send_message(
                connection,
                {"type": "session_resume_rejected", "reason": "invalid_or_expired_token"},
            )
            return
        task = self._disconnect_tasks.pop(result.user.id, None)
        if task is not None:
            task.cancel()
        self._authenticated_users[connection] = result.user
        self._sessions.assign(connection, result.color)
        self._log(
            logging.INFO,
            "session_resumed",
            game_id=result.game_id,
            user_id=result.user.id,
            username=result.user.username,
        )
        await self._send_message(
            connection,
            {
                "type": "session_resumed",
                "game_id": result.game_id,
                "color": result.color.name.lower(),
            },
        )
        await self._send_message(
            connection,
            {"type": "session_resume_token", "token": result.token},
        )
        await self._send_snapshot(connection)
        await self._send_message(
            connection,
            {"type": "player_profiles", "players": self._profile_payloads()},
        )
        if result.opponent_connection is not None:
            await self._send_message(
                cast(ClientConnection, result.opponent_connection),
                {
                    "type": "opponent_reconnected",
                    "game_id": result.game_id,
                    "username": result.user.username,
                },
            )

    async def _wait_for_disconnect_timeout(self, notice: DisconnectNotice) -> None:
        delay = max(0.0, notice.deadline - datetime.now(timezone.utc).timestamp())
        try:
            await asyncio.sleep(delay)
        except asyncio.CancelledError:
            return
        result = self._reconnect.expire(notice.user.id, notice.deadline)
        if result is None:
            return
        self._log(
            logging.WARNING,
            "reconnect_timeout",
            game_id=result.game_id,
            user_id=notice.user.id,
            username=notice.user.username,
        )
        if result.winner_color is not None:
            await self._finalize_ratings(result.winner_color)
        message: dict[str, JsonValue] = {
            "type": "disconnect_forfeit",
            "game_id": result.game_id,
            "winner": result.winner.username if result.winner else None,
            "loser": result.loser.username if result.loser else None,
            "reason": "reconnect_timeout",
        }
        for target in result.connections:
            await self._send_message(cast(ClientConnection, target), message)
        self._log(
            logging.WARNING,
            "disconnect_forfeit",
            game_id=result.game_id,
            username=result.loser.username if result.loser else None,
        )
        for target in result.connections:
            self._sessions.disconnect(target)
            self._matchmaking.disconnect(target)
            self._authenticated_users.pop(target, None)
        self._reconnect.cleanup()
        await self._close_spectator_views(result.game_id)
        self._game_users_by_color.clear()

    async def _accept_game_client(self, connection: ClientConnection) -> bool:
        color = self._sessions.connect(connection)
        if color is None:
            self._logger.info("Rejected client connection: game is full")
            await self._send_message(
                connection,
                {"type": "connection_rejected", "reason": "game_full"},
            )
            return False
        self._logger.info("Client accepted with color %s", color.name)
        await self._send_message(
            connection,
            {"type": "connection_accepted", "color": color.name.lower()},
        )
        await self._send_snapshot(connection)
        return True

    @staticmethod
    def _authentication_response(
        response_type: str,
        user: User,
    ) -> dict[str, JsonValue]:
        return {
            "type": response_type,
            "username": user.username,
            "rating": user.rating,
        }

    async def broadcast_snapshot(self) -> None:
        """Broadcast the current authoritative game snapshot."""
        await self.broadcast(
            {
                "type": "game_snapshot",
                "state": self._snapshot_serializer.serialize(self._game_engine),
            }
        )

    async def broadcast(self, message: dict[str, JsonValue]) -> None:
        """Send one JSON-safe message to all currently accepted clients."""
        encoded = json.dumps(message)
        recipients = dict.fromkeys(
            (*self._sessions.clients, *self._spectators.spectators_for(self._game_id))
        )
        clients = cast(tuple[ClientConnection, ...], tuple(recipients))
        if not clients:
            return
        await asyncio.gather(
            *(self._send_encoded(client, encoded) for client in clients)
        )

    async def run(self, host: str, port: int) -> None:
        """Listen for local WebSocket clients until the task is cancelled."""
        self._loop = asyncio.get_running_loop()
        simulation_task = asyncio.create_task(self._run_simulation())
        self._log(logging.INFO, "server_started", reason=f"{host}:{port}")
        try:
            async with serve(self.handle_client, host, port) as server:
                await server.serve_forever()
        finally:
            simulation_task.cancel()
            await asyncio.gather(simulation_task, return_exceptions=True)
            self._log(logging.INFO, "server_stopped")

    def _execute_command(
        self,
        connection: ClientConnection,
        command: NetworkCommand,
    ) -> dict[str, JsonValue]:
        if self._game_engine.game_over:
            return self._rejection("game_over")

        position = command.source if isinstance(command, MoveCommand) else command.position
        piece = self._controlled_piece(connection, position)
        if isinstance(piece, str):
            return self._rejection(piece)

        if isinstance(command, LegalMovesCommand):
            legal_moves = self._game_engine.get_legal_moves(command.position)
            return {
                "type": "legal_moves",
                "source": self._serialize_position(command.position),
                "positions": [
                    self._serialize_position(position)
                    for position in sorted(
                        legal_moves,
                        key=lambda item: (item.row, item.column),
                    )
                ],
            }

        if isinstance(command, MoveCommand):
            result = self._game_engine.request_move(command.source, command.target)
            if not result.is_accepted:
                return self._rejection(result.reason.value)
            return {"type": "command_accepted", "command": "move"}

        try:
            self._game_engine.jump(command.position)
        except UserInputError:
            return self._rejection("illegal_jump")
        return {"type": "command_accepted", "command": "jump"}

    def _controlled_piece(
        self,
        connection: ClientConnection,
        position: Position,
    ) -> Piece | str:
        if not self._game_engine.is_inside(position):
            return "missing_piece"
        piece = self._game_engine.get_piece(position)
        if not isinstance(piece, Piece):
            return "missing_piece"
        if not self._sessions.can_control(connection, piece.color):
            return "not_your_piece"
        return piece

    async def _run_simulation(self) -> None:
        loop = asyncio.get_running_loop()
        previous_time = loop.time()
        while True:
            await asyncio.sleep(self._SIMULATION_INTERVAL_SECONDS)
            current_time = loop.time()
            elapsed = max(1, int((current_time - previous_time) * 1000))
            previous_time = current_time
            async with self._command_lock:
                before = self._snapshot_serializer.serialize(self._game_engine)
                self._game_engine.wait(elapsed)
                after = self._snapshot_serializer.serialize(self._game_engine)
            if after != before:
                await self.broadcast(
                    {"type": "game_snapshot", "state": after}
                )

    def _subscribe_to_game_events(self) -> None:
        for event_type in self._OBSERVED_EVENT_TYPES:
            self._game_engine.event_bus.subscribe(event_type, self._on_game_event)

    def _on_game_event(self, event: Event) -> None:
        message: dict[str, JsonValue] = {
            "type": "game_event",
            "event_id": self._next_event_id,
            "event": self._event_serializer.serialize(event),
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
        task = loop.create_task(self.broadcast(message))
        self._broadcast_tasks.add(task)
        task.add_done_callback(self._broadcast_tasks.discard)
        if (
            isinstance(event, GameOverEvent)
            and not self._rating_finalization_started
        ):
            self._log(
                logging.INFO,
                "game_over",
                game_id=self._game_id,
            )
            self._rating_finalization_started = True
            rating_task = loop.create_task(self._finish_completed_game(event.winner))
            self._broadcast_tasks.add(rating_task)
            rating_task.add_done_callback(self._broadcast_tasks.discard)

    async def _finish_completed_game(self, winner: PieceColor | None) -> None:
        if winner is not None:
            await self._finalize_ratings(winner)
        await self._close_spectator_views(self._game_id)

    async def _close_spectator_views(self, game_id: str) -> None:
        spectators = self._spectators.close_game(game_id)
        for spectator in spectators:
            await self._send_message(
                cast(ClientConnection, spectator),
                {"type": "spectating_stopped", "reason": "game_ended"},
            )

    async def _finalize_ratings(self, winner_color: PieceColor) -> None:
        service = self._rating_service
        if service is None:
            return
        players = self._users_by_color()
        winner = players.get(winner_color)
        loser_color = (
            PieceColor.BLACK
            if winner_color is PieceColor.WHITE
            else PieceColor.WHITE
        )
        loser = players.get(loser_color)
        if winner is None or loser is None:
            return
        try:
            update = await asyncio.to_thread(
                service.record_result,
                self._game_id,
                winner,
                loser,
            )
        except Exception:
            self._logger.exception("Failed to persist multiplayer ratings")
            await self.broadcast({"type": "server_error"})
            return
        if update is None:
            return
        self._replace_authenticated_user(update.winner)
        self._replace_authenticated_user(update.loser)
        await self._broadcast_rating_update(update)
        self._log(
            logging.INFO,
            "elo_ratings_updated",
            game_id=self._game_id,
            user_id=update.winner.id,
            username=update.winner.username,
        )

    async def _broadcast_player_profiles(self, message_type: str) -> None:
        profiles = self._profile_payloads()
        if len(profiles) != 2:
            return
        await self.broadcast({"type": message_type, "players": profiles})

    async def _broadcast_rating_update(self, update: RatingUpdate) -> None:
        changes = {
            update.winner.id: update.winner_change,
            update.loser.id: update.loser_change,
        }
        await self.broadcast(
            {
                "type": "rating_updated",
                "players": self._profile_payloads(changes),
            }
        )

    def _profile_payloads(
        self,
        rating_changes: dict[int, int] | None = None,
    ) -> list[JsonValue]:
        profiles: list[JsonValue] = []
        users = self._users_by_color()
        for color in (PieceColor.WHITE, PieceColor.BLACK):
            user = users.get(color)
            if user is None:
                continue
            profile: dict[str, JsonValue] = {
                "username": user.username,
                "color": color.name.lower(),
                "rating": user.rating,
            }
            if rating_changes is not None:
                profile["rating_change"] = rating_changes[user.id]
            profiles.append(profile)
        return profiles

    def _users_by_color(self) -> dict[PieceColor, User]:
        users: dict[PieceColor, User] = dict(self._game_users_by_color)
        for connection, user in self._authenticated_users.items():
            color = self._sessions.color_for(connection)
            if color is not None:
                users[color] = user
        return users

    def _replace_authenticated_user(self, updated_user: User) -> None:
        for color, user in self._game_users_by_color.items():
            if user.id == updated_user.id:
                self._game_users_by_color[color] = updated_user
                break
        for connection, user in self._authenticated_users.items():
            if user.id == updated_user.id:
                self._authenticated_users[connection] = updated_user
                return

    @staticmethod
    def _decode_message(raw_message: str | bytes) -> dict[str, object]:
        decoded = json.loads(raw_message)
        if not isinstance(decoded, dict):
            raise CommandParseError("Command JSON must contain an object.")
        return decoded

    async def _send_snapshot(self, connection: ClientConnection) -> None:
        await self._send_message(
            connection,
            {
                "type": "game_snapshot",
                "state": self._snapshot_serializer.serialize(self._game_engine),
            },
        )

    async def _reject(self, connection: ClientConnection, reason: str) -> None:
        self._logger.info("Rejected client command: %s", reason)
        await self._send_message(connection, self._rejection(reason))

    @staticmethod
    def _rejection(reason: str) -> dict[str, JsonValue]:
        return {"type": "command_rejected", "reason": reason}

    @staticmethod
    def _serialize_position(position: Position) -> dict[str, JsonValue]:
        return {"row": position.row, "column": position.column}

    async def _send_message(
        self,
        connection: ClientConnection,
        message: dict[str, JsonValue],
    ) -> None:
        await self._send_encoded(connection, json.dumps(message))

    async def _send_encoded(
        self,
        connection: ClientConnection,
        encoded_message: str,
    ) -> None:
        try:
            await connection.send(encoded_message)
        except Exception:
            self._sessions.disconnect(connection)
            self._logger.warning(
                "Removed client after a failed WebSocket send",
                exc_info=True,
            )

    def _log(self, level: int, event_type: str, **context: object) -> None:
        """Emit one structured server event without transport-sensitive data."""
        safe_context = {
            key: value for key, value in context.items() if value is not None
        }
        self._logger.log(
            level,
            event_type,
            extra={"event_type": event_type, **safe_context},
        )
