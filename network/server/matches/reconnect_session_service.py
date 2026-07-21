"""Connection-independent ownership for resumable multiplayer sessions."""

from dataclasses import dataclass
from enum import Enum
import secrets
import threading
import time
from collections.abc import Callable

from authentication.user import User
from model.piece import PieceColor


class ParticipantConnectionState(Enum):
    """Server-side connectivity state for a matched participant."""

    CONNECTED = "connected"
    DISCONNECTED_WAITING = "disconnected_waiting"
    FORFEITED = "forfeited"


@dataclass
class GameParticipant:
    """Mutable server-only connection data for one immutable game identity."""

    user: User
    color: PieceColor
    connection: object | None
    token: str
    state: ParticipantConnectionState = ParticipantConnectionState.CONNECTED
    disconnect_deadline: float | None = None


@dataclass(frozen=True)
class DisconnectNotice:
    """Facts needed to notify an opponent and schedule expiry."""

    game_id: str
    user: User
    color: PieceColor
    deadline: float
    opponent_connection: object | None


@dataclass(frozen=True)
class ResumeResult:
    """Validated attachment of a new connection to an existing participant."""

    game_id: str
    user: User
    color: PieceColor
    token: str
    opponent_connection: object | None


@dataclass(frozen=True)
class ExpiryResult:
    """Idempotent terminal result produced by one expired deadline."""

    game_id: str
    loser: User | None
    winner: User | None
    winner_color: PieceColor | None
    connections: tuple[object, ...]


class ReconnectSessionService:
    """Owns resume tokens, participant connections, and reconnect deadlines."""

    def __init__(
        self,
        timeout_seconds: float = 20.0,
        clock: Callable[[], float] = time.time,
    ) -> None:
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self.timeout_seconds = timeout_seconds
        self._clock = clock
        self._game_id: str | None = None
        self._participants: dict[int, GameParticipant] = {}
        self._user_by_connection: dict[object, int] = {}
        self._user_by_token: dict[str, int] = {}
        self._completed = False
        self._lock = threading.RLock()

    def create_game(
        self,
        game_id: str,
        participants: tuple[tuple[object, User, PieceColor], ...],
    ) -> dict[object, str]:
        """Register one active game and issue opaque tokens to both clients."""
        with self._lock:
            self._game_id = game_id
            self._participants.clear()
            self._user_by_connection.clear()
            self._user_by_token.clear()
            self._completed = False
            tokens: dict[object, str] = {}
            for connection, user, color in participants:
                token = secrets.token_urlsafe(32)
                participant = GameParticipant(user, color, connection, token)
                self._participants[user.id] = participant
                self._user_by_connection[connection] = user.id
                self._user_by_token[token] = user.id
                tokens[connection] = token
            return tokens

    def disconnect(self, connection: object) -> DisconnectNotice | None:
        """Mark the current participant connection as temporarily absent."""
        with self._lock:
            user_id = self._user_by_connection.pop(connection, None)
            if user_id is None or self._completed or self._game_id is None:
                return None
            participant = self._participants[user_id]
            if participant.connection is not connection:
                return None
            deadline = self._clock() + self.timeout_seconds
            participant.connection = None
            participant.state = ParticipantConnectionState.DISCONNECTED_WAITING
            participant.disconnect_deadline = deadline
            opponent = self._opponent(user_id)
            return DisconnectNotice(
                self._game_id,
                participant.user,
                participant.color,
                deadline,
                opponent.connection if opponent is not None else None,
            )

    def resume(self, connection: object, token: object) -> ResumeResult | None:
        """Validate an opaque token and atomically attach a replacement socket."""
        if not isinstance(token, str):
            return None
        with self._lock:
            user_id = self._user_by_token.get(token)
            if user_id is None or self._completed or self._game_id is None:
                return None
            participant = self._participants[user_id]
            deadline = participant.disconnect_deadline
            if (
                participant.state is not ParticipantConnectionState.DISCONNECTED_WAITING
                or deadline is None
                or self._clock() > deadline
                or participant.connection is not None
            ):
                return None
            self._user_by_token.pop(token, None)
            rotated_token = secrets.token_urlsafe(32)
            participant.token = rotated_token
            participant.connection = connection
            participant.state = ParticipantConnectionState.CONNECTED
            participant.disconnect_deadline = None
            self._user_by_token[rotated_token] = user_id
            self._user_by_connection[connection] = user_id
            opponent = self._opponent(user_id)
            return ResumeResult(
                self._game_id,
                participant.user,
                participant.color,
                rotated_token,
                opponent.connection if opponent is not None else None,
            )

    def expire(self, user_id: int, deadline: float) -> ExpiryResult | None:
        """Finalize a still-current deadline once; stale callbacks are harmless."""
        with self._lock:
            participant = self._participants.get(user_id)
            if participant is None or self._completed:
                return None
            if (
                participant.state is not ParticipantConnectionState.DISCONNECTED_WAITING
                or participant.disconnect_deadline != deadline
                or self._clock() < deadline
            ):
                return None
            opponent = self._opponent(user_id)
            self._completed = True
            participant.state = ParticipantConnectionState.FORFEITED
            connections = tuple(
                item.connection
                for item in self._participants.values()
                if item.connection is not None
            )
            if opponent is None or opponent.connection is None:
                return ExpiryResult(self._game_id or "", None, None, None, connections)
            return ExpiryResult(
                self._game_id or "",
                participant.user,
                opponent.user,
                opponent.color,
                connections,
            )

    def is_paused(self) -> bool:
        with self._lock:
            return any(
                participant.state is ParticipantConnectionState.DISCONNECTED_WAITING
                for participant in self._participants.values()
            )

    def participant_for_connection(self, connection: object) -> GameParticipant | None:
        with self._lock:
            user_id = self._user_by_connection.get(connection)
            return self._participants.get(user_id) if user_id is not None else None

    def cleanup(self) -> None:
        """Invalidate all tokens and release completed session references."""
        with self._lock:
            self._participants.clear()
            self._user_by_connection.clear()
            self._user_by_token.clear()
            self._game_id = None

    def _opponent(self, user_id: int) -> GameParticipant | None:
        return next(
            (item for key, item in self._participants.items() if key != user_id),
            None,
        )
