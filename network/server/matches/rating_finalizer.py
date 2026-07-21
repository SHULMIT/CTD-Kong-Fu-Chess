"""Idempotent multiplayer ELO persistence and profile presentation."""

import asyncio
import logging
from collections.abc import Callable

from authentication.user import User
from model.piece import PieceColor
from network.server.authentication_handler import AuthenticationHandler
from network.server.transport.client_messenger import ClientMessenger
from network.server.transport.game_snapshot_serializer import JsonValue
from network.server.matches.session_manager import SessionManager
from rating.persistent_rating_service import PersistentRatingService, RatingUpdate


class RatingFinalizer:
    """Owns current player profiles and persists each decisive result once."""

    def __init__(
        self,
        service: PersistentRatingService | None,
        authentication: AuthenticationHandler,
        sessions: SessionManager,
        messenger: ClientMessenger,
        game_id_provider: Callable[[], str],
        logger: logging.Logger,
    ) -> None:
        self._service = service
        self._authentication = authentication
        self._sessions = sessions
        self._messenger = messenger
        self._game_id_provider = game_id_provider
        self._logger = logger
        self.game_users_by_color: dict[PieceColor, User] = {}

    def set_players(self, white: User, black: User) -> None:
        self.game_users_by_color.clear()
        self.game_users_by_color.update(
            {PieceColor.WHITE: white, PieceColor.BLACK: black}
        )

    def clear(self) -> None:
        self.game_users_by_color.clear()

    async def finalize(self, winner_color: PieceColor) -> None:
        """Persist and broadcast one authoritative rating result."""
        if self._service is None:
            return
        players = self.users_by_color()
        winner = players.get(winner_color)
        loser_color = (
            PieceColor.BLACK if winner_color is PieceColor.WHITE else PieceColor.WHITE
        )
        loser = players.get(loser_color)
        if winner is None or loser is None:
            return
        game_id = self._game_id_provider()
        try:
            update = await asyncio.to_thread(
                self._service.record_result, game_id, winner, loser
            )
        except Exception:
            self._logger.exception("Failed to persist multiplayer ratings")
            await self._messenger.broadcast({"type": "server_error"})
            return
        if update is None:
            return
        self.replace_user(update.winner)
        self.replace_user(update.loser)
        await self._broadcast_update(update)
        self._logger.info(
            "elo_ratings_updated",
            extra={
                "event_type": "elo_ratings_updated",
                "game_id": game_id,
                "user_id": update.winner.id,
                "username": update.winner.username,
            },
        )

    def profiles(
        self,
        rating_changes: dict[int, int] | None = None,
    ) -> list[JsonValue]:
        profiles: list[JsonValue] = []
        users = self.users_by_color()
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

    def users_by_color(self) -> dict[PieceColor, User]:
        users = dict(self.game_users_by_color)
        for connection, user in self._authentication.users.items():
            color = self._sessions.color_for(connection)
            if color is not None:
                users[color] = user
        return users

    def replace_user(self, updated_user: User) -> None:
        for color, user in self.game_users_by_color.items():
            if user.id == updated_user.id:
                self.game_users_by_color[color] = updated_user
                break
        self._authentication.replace(updated_user)

    async def _broadcast_update(self, update: RatingUpdate) -> None:
        changes = {
            update.winner.id: update.winner_change,
            update.loser.id: update.loser_change,
        }
        await self._messenger.broadcast(
            {"type": "rating_updated", "players": self.profiles(changes)}
        )
