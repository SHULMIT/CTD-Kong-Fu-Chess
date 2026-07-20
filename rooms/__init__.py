"""Transport-independent private room management."""

from rooms.private_room_service import (
    PrivateRoom,
    PrivateRoomError,
    PrivateRoomErrorCode,
    PrivateRoomService,
    RoomMatch,
    RoomStatus,
)

__all__ = [
    "PrivateRoom",
    "PrivateRoomError",
    "PrivateRoomErrorCode",
    "PrivateRoomService",
    "RoomMatch",
    "RoomStatus",
]
