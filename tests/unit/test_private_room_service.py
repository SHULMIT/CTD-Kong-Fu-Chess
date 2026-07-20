"""Focused tests for transport-independent private room lifecycle."""

import pytest

from authentication.user import User
from rooms.private_room_service import (
    PrivateRoomError,
    PrivateRoomErrorCode,
    PrivateRoomService,
    RoomStatus,
)


def test_creation_uses_unique_short_codes() -> None:
    codes = iter(("ABC123", "ABC123", "XYZ789"))
    service = PrivateRoomService(code_factory=lambda _length: next(codes))

    first = service.create(object(), User(1, "Dan", 1200))
    second = service.create(object(), User(2, "Noa", 1210))

    assert first.code == "ABC123"
    assert second.code == "XYZ789"
    assert len(first.code) == 6


def test_join_fills_room_once_and_prevents_duplicate_player() -> None:
    service = PrivateRoomService(code_factory=lambda _length: "AB42KF")
    creator, guest = object(), object()
    service.create(creator, User(1, "Dan", 1200))

    with pytest.raises(PrivateRoomError) as duplicate:
        service.join("AB42KF", object(), User(1, "Dan", 1200))
    assert duplicate.value.code is PrivateRoomErrorCode.INVALID_STATE

    match = service.join("ab42kf", guest, User(2, "Noa", 1210))
    assert match.creator_connection is creator
    assert match.guest_connection is guest
    assert match.game_id
    with pytest.raises(PrivateRoomError) as full:
        service.join("AB42KF", object(), User(3, "Avi", 1190))
    assert full.value.code is PrivateRoomErrorCode.FULL_ROOM


def test_unknown_closed_cancel_and_creator_disconnect_cleanup() -> None:
    service = PrivateRoomService(code_factory=lambda _length: "ROOM42")
    creator = object()
    with pytest.raises(PrivateRoomError) as unknown:
        service.join("NOPE42", object(), User(2, "Noa", 1200))
    assert unknown.value.code is PrivateRoomErrorCode.UNKNOWN_ROOM

    room = service.create(creator, User(1, "Dan", 1200))
    assert service.cancel(creator) == room.code
    assert service.room(room.code).status is RoomStatus.CLOSED
    with pytest.raises(PrivateRoomError) as closed:
        service.join(room.code, object(), User(2, "Noa", 1200))
    assert closed.value.code is PrivateRoomErrorCode.CLOSED_ROOM

    another = PrivateRoomService(code_factory=lambda _length: "ROOM43")
    owner = object()
    another.create(owner, User(3, "Avi", 1200))
    assert another.disconnect(owner) == "ROOM43"
    assert another.room("ROOM43").status is RoomStatus.CLOSED
