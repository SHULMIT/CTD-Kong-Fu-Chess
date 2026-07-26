"""Interpret decoded server messages and update client session state."""

from __future__ import annotations

import json
import queue
from typing import Any

from model.piece import PieceColor
from network.client_session_state import ClientSessionState, MultiplayerClientState


class ServerMessageHandler:
    """Route server messages without owning a network connection."""

    _AUTHENTICATION_TYPES = frozenset({
        "registration_success", "login_success", "username_taken",
        "invalid_credentials", "validation_error", "server_error",
        "connection_rejected", "already_authenticated",
    })

    def __init__(
        self,
        session: ClientSessionState,
        messages: queue.Queue[dict[str, Any]],
        authentication_responses: queue.Queue[dict[str, Any]],
    ) -> None:
        self._session = session
        self._messages = messages
        self._authentication_responses = authentication_responses

    def handle_raw(self, raw_message: str | bytes) -> None:
        """Decode one raw JSON message, then route its decoded form."""
        try:
            message = json.loads(raw_message)
        except (json.JSONDecodeError, UnicodeDecodeError):
            message = {"type": "server_error"}
        self.handle(message if isinstance(message, dict) else {"type": "server_error"})

    def handle(self, message: dict[str, Any]) -> None:
        """Update state and publish a message to consumers."""
        message_type = message.get("type")
        with self._session._lock:
            if message_type in self._AUTHENTICATION_TYPES:
                if message_type == "login_success":
                    self._session.username = str(message.get("username"))
                    rating = message.get("rating")
                    self._session.rating = rating if type(rating) is int else None
                self._authentication_responses.put(message)
            if message_type == "connection_accepted":
                try:
                    self._session.assigned_color = PieceColor[str(message.get("color")).upper()]
                except KeyError:
                    pass
                else:
                    self._session.matchmaking_state = MultiplayerClientState.IN_GAME
            elif message_type == "game_snapshot" and isinstance(message.get("state"), dict):
                self._session.initial_snapshot = message["state"]
            elif message_type == "rating_updated" and self._session.assigned_color is not None:
                for profile in message.get("players", []):
                    if profile.get("color") == self._session.assigned_color.name.lower():
                        rating = profile.get("rating")
                        if type(rating) is int:
                            self._session.rating = rating
            elif message_type == "matchmaking_queued":
                self._session.matchmaking_state = MultiplayerClientState.SEARCHING
                rating = message.get("rating")
                if type(rating) is int:
                    self._session.rating = rating
            elif message_type == "matchmaking_canceled":
                self._session.matchmaking_state = MultiplayerClientState.IDLE
            elif message_type == "match_found":
                self._session.matchmaking_state = MultiplayerClientState.MATCHED
                self._session.match_found = message
            elif message_type == "room_created":
                self._session.matchmaking_state = MultiplayerClientState.ROOM_WAITING
            elif message_type == "room_closed":
                self._session.matchmaking_state = MultiplayerClientState.IDLE
            elif message_type == "spectating_started":
                self._session.matchmaking_state = MultiplayerClientState.SPECTATING
            elif message_type == "spectating_stopped":
                self._session.matchmaking_state = MultiplayerClientState.IDLE
            elif message_type == "player_profiles":
                self._session.player_profiles = message
            elif message_type == "session_resume_token" and isinstance(message.get("token"), str):
                self._session.resume_token = message["token"]
            elif message_type == "session_resumed":
                try:
                    self._session.assigned_color = PieceColor[str(message.get("color")).upper()]
                except KeyError:
                    return
                self._session.matchmaking_state = MultiplayerClientState.IN_GAME
                self._session.resume_completed = True
        self._messages.put(message)
