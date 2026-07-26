"""Thread-safe client-side state derived from server messages."""

from __future__ import annotations

import threading
from enum import Enum
from typing import Any

from model.piece import PieceColor


class MultiplayerClientState(Enum):
    """Client presentation state; the server remains authoritative."""

    IDLE = "idle"
    SEARCHING = "searching"
    ROOM_WAITING = "room_waiting"
    MATCHED = "matched"
    IN_GAME = "in_game"
    SPECTATING = "spectating"


class ClientSessionState:
    """Own mutable session data and synchronize access from UI and IO threads."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self.reset()

    def reset(self) -> None:
        """Clear all state associated with an intentional session end."""
        with self._lock:
            self.username: str | None = None
            self.rating: int | None = None
            self.assigned_color: PieceColor | None = None
            self.initial_snapshot: dict[str, Any] | None = None
            self.matchmaking_state = MultiplayerClientState.IDLE
            self.match_found: dict[str, Any] | None = None
            self.player_profiles: dict[str, Any] | None = None
            self.resume_token: str | None = None
            self.resume_completed = False

    def set_matchmaking_state(self, state: MultiplayerClientState) -> None:
        """Set the locally observed lobby state."""
        with self._lock:
            self.matchmaking_state = state

    def resume_token_value(self) -> str | None:
        """Return the latest token safely for the reconnecting transport."""
        with self._lock:
            return self.resume_token

    def consume_resume_completed(self) -> bool:
        """Return and clear the reconnect acknowledgement flag."""
        with self._lock:
            completed = self.resume_completed
            self.resume_completed = False
            return completed
