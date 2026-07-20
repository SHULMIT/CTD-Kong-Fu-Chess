"""Thread-safe private room lifecycle without transport or game dependencies."""

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
import secrets
import string
import threading
from uuid import uuid4

from authentication.user import User


class RoomStatus(Enum):
    """Lifecycle of a private room code."""

    OPEN = "open"
    FULL = "full"
    CLOSED = "closed"


class PrivateRoomErrorCode(Enum):
    """Stable domain errors translated by the WebSocket boundary."""

    UNKNOWN_ROOM = "unknown_room_code"
    FULL_ROOM = "full_room"
    CLOSED_ROOM = "closed_room"
    INVALID_STATE = "invalid_state"


class PrivateRoomError(ValueError):
    """Reports a rejected room operation without transport details."""

    def __init__(self, code: PrivateRoomErrorCode) -> None:
        super().__init__(code.value)
        self.code = code


@dataclass
class PrivateRoom:
    """Server-owned waiting room with one authenticated creator."""

    code: str
    creator_connection: object
    creator: User
    status: RoomStatus = RoomStatus.OPEN


@dataclass(frozen=True)
class RoomMatch:
    """The single pairing produced when a guest fills an open room."""

    game_id: str
    room_code: str
    creator_connection: object
    creator: User
    guest_connection: object
    guest: User


class PrivateRoomService:
    """Creates short room codes and atomically fills each room once."""

    _ALPHABET = string.ascii_uppercase + string.digits

    def __init__(
        self,
        code_length: int = 6,
        code_factory: Callable[[int], str] | None = None,
    ) -> None:
        if code_length < 4:
            raise ValueError("code_length must be at least four")
        self._code_length = code_length
        self._code_factory = code_factory or self._secure_code
        self._rooms: dict[str, PrivateRoom] = {}
        self._room_by_client: dict[object, str] = {}
        self._lock = threading.RLock()

    def create(self, connection: object, user: User) -> PrivateRoom:
        """Create one open room for a client that is not already in a room."""
        with self._lock:
            if connection in self._room_by_client:
                raise PrivateRoomError(PrivateRoomErrorCode.INVALID_STATE)
            code = self._unique_code()
            room = PrivateRoom(code, connection, user)
            self._rooms[code] = room
            self._room_by_client[connection] = code
            return room

    def join(self, code: object, connection: object, user: User) -> RoomMatch:
        """Atomically fill an open room and return exactly one game pairing."""
        if not isinstance(code, str):
            raise PrivateRoomError(PrivateRoomErrorCode.UNKNOWN_ROOM)
        normalized = code.strip().upper()
        with self._lock:
            if connection in self._room_by_client:
                raise PrivateRoomError(PrivateRoomErrorCode.INVALID_STATE)
            room = self._rooms.get(normalized)
            if room is None:
                raise PrivateRoomError(PrivateRoomErrorCode.UNKNOWN_ROOM)
            if room.status is RoomStatus.CLOSED:
                raise PrivateRoomError(PrivateRoomErrorCode.CLOSED_ROOM)
            if room.status is RoomStatus.FULL:
                raise PrivateRoomError(PrivateRoomErrorCode.FULL_ROOM)
            if room.creator_connection == connection or room.creator.id == user.id:
                raise PrivateRoomError(PrivateRoomErrorCode.INVALID_STATE)
            room.status = RoomStatus.FULL
            self._room_by_client[connection] = normalized
            return RoomMatch(
                str(uuid4()),
                normalized,
                room.creator_connection,
                room.creator,
                connection,
                user,
            )

    def cancel(self, creator_connection: object) -> str:
        """Close an open room owned by its creator."""
        with self._lock:
            code = self._room_by_client.get(creator_connection)
            room = self._rooms.get(code) if code is not None else None
            if (
                room is None
                or room.creator_connection != creator_connection
                or room.status is not RoomStatus.OPEN
            ):
                raise PrivateRoomError(PrivateRoomErrorCode.INVALID_STATE)
            room.status = RoomStatus.CLOSED
            self._room_by_client.pop(creator_connection, None)
            return room.code

    def disconnect(self, connection: object) -> str | None:
        """Close an abandoned open room and release client membership."""
        with self._lock:
            code = self._room_by_client.pop(connection, None)
            room = self._rooms.get(code) if code is not None else None
            if room is None:
                return None
            if room.creator_connection == connection and room.status is RoomStatus.OPEN:
                room.status = RoomStatus.CLOSED
                return room.code
            return None

    def contains(self, connection: object) -> bool:
        """Return whether a client currently owns or occupies a room."""
        with self._lock:
            return connection in self._room_by_client

    def release_match(self, room_code: str) -> None:
        """Release connection membership after the game session takes ownership."""
        with self._lock:
            room = self._rooms.get(room_code)
            if room is None:
                return
            for connection, code in tuple(self._room_by_client.items()):
                if code == room_code:
                    self._room_by_client.pop(connection, None)

    def room(self, code: str) -> PrivateRoom | None:
        """Return a room for diagnostics without exposing the room collection."""
        with self._lock:
            return self._rooms.get(code)

    def _unique_code(self) -> str:
        for _ in range(100):
            code = self._code_factory(self._code_length).upper()
            if code not in self._rooms:
                return code
        raise RuntimeError("Unable to generate a unique room code")

    @classmethod
    def _secure_code(cls, length: int) -> str:
        return "".join(secrets.choice(cls._ALPHABET) for _ in range(length))
