"""Thread-safe, transport-independent ELO matchmaking."""

from dataclasses import dataclass
from enum import Enum
import threading
from uuid import uuid4

from authentication.user import User


class MatchmakingState(Enum):
    """Lifecycle state of one client in matchmaking.

    מייצגת את רכיב השרת ``MatchmakingState`` ומרכזת את התנהגותו.

    Responsibility: Lifecycle state of one client in matchmaking.

    אחריות: מייצגת את רכיב השרת ``MatchmakingState`` ומרכזת את התנהגותו."""

    IDLE = "idle"
    QUEUED = "queued"
    MATCHED = "matched"
    IN_GAME = "in_game"


@dataclass(frozen=True)
class MatchmakingEntry:
    """One authenticated client waiting with an authoritative user profile.

    מייצגת את רכיב השרת ``MatchmakingEntry`` ומרכזת את התנהגותו.

    Responsibility: One authenticated client waiting with an authoritative user profile.

    אחריות: מייצגת את רכיב השרת ``MatchmakingEntry`` ומרכזת את התנהגותו."""

    client: object
    user: User


@dataclass(frozen=True)
class Match:
    """An atomically created pairing; the older entry receives white.

    מייצגת את רכיב השרת ``Match`` ומרכזת את התנהגותו.

    Responsibility: An atomically created pairing; the older entry receives white.

    אחריות: מייצגת את רכיב השרת ``Match`` ומרכזת את התנהגותו."""

    game_id: str
    white: MatchmakingEntry
    black: MatchmakingEntry


class MatchmakingService:
    """Pairs queued users whose authoritative ratings differ by at most 100.

    מייצגת את רכיב השרת ``MatchmakingService`` ומרכזת את התנהגותו.

    Responsibility: Pairs queued users whose authoritative ratings differ by at most 100.

    אחריות: מייצגת את רכיב השרת ``MatchmakingService`` ומרכזת את התנהגותו."""

    def __init__(self, maximum_rating_difference: int = 100) -> None:
        """Initialize the instance and its dependencies.

        מאתחלת את המופע ואת התלויות שלו."""
        if maximum_rating_difference < 0:
            raise ValueError("maximum_rating_difference cannot be negative")
        self._maximum_rating_difference = maximum_rating_difference
        self._queue: list[MatchmakingEntry] = []
        self._states: dict[object, MatchmakingState] = {}
        self._lock = threading.RLock()

    def enqueue(self, client: object, user: User) -> Match | None:
        """Queue a client or atomically return one compatible match.

        מבצעת את פעולת ``enqueue``."""
        with self._lock:
            state = self._states.get(client, MatchmakingState.IDLE)
            if state is not MatchmakingState.IDLE:
                return None

            opponent = self._find_opponent(client, user)
            if opponent is None:
                self._queue.append(MatchmakingEntry(client, user))
                self._states[client] = MatchmakingState.QUEUED
                return None

            self._queue.remove(opponent)
            challenger = MatchmakingEntry(client, user)
            self._states[opponent.client] = MatchmakingState.MATCHED
            self._states[client] = MatchmakingState.MATCHED
            return Match(str(uuid4()), opponent, challenger)

    def cancel(self, client: object) -> bool:
        """Remove a queued client; matched or in-game clients are unchanged.

        מבצעת את פעולת ``cancel``."""
        with self._lock:
            if self._states.get(client) is not MatchmakingState.QUEUED:
                return False
            self._queue = [entry for entry in self._queue if entry.client != client]
            self._states[client] = MatchmakingState.IDLE
            return True

    def disconnect(self, client: object) -> None:
        """Ensure a disconnected waiting client can never be matched later.

        מבצעת את פעולת ``disconnect``."""
        with self._lock:
            self._queue = [entry for entry in self._queue if entry.client != client]
            self._states.pop(client, None)

    def mark_in_game(self, client: object) -> None:
        """Advance a matched client to the in-game state.

        מבצעת את פעולת ``mark`` ``in`` המשחק."""
        with self._lock:
            if self._states.get(client) is MatchmakingState.MATCHED:
                self._states[client] = MatchmakingState.IN_GAME

    def state_for(self, client: object) -> MatchmakingState:
        """Return a stable state snapshot for a client.

        מבצעת את פעולת המצב ``for``."""
        with self._lock:
            return self._states.get(client, MatchmakingState.IDLE)

    @property
    def queued_entries(self) -> tuple[MatchmakingEntry, ...]:
        """Return an immutable queue snapshot for diagnostics and tests.

        מבצעת את פעולת ``queued`` ``entries``."""
        with self._lock:
            return tuple(self._queue)

    def _find_opponent(
        self,
        client: object,
        user: User,
    ) -> MatchmakingEntry | None:
        """Find and return opponent.

        מאתרת ומחזירה את ``opponent``."""
        for entry in self._queue:
            if entry.client == client or entry.user.id == user.id:
                continue
            if abs(entry.user.rating - user.rating) <= self._maximum_rating_difference:
                return entry
        return None
