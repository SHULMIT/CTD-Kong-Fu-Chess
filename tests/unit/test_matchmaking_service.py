"""Focused tests for transport-independent ELO matchmaking."""

from concurrent.futures import ThreadPoolExecutor

import pytest

from authentication.user import User
from matchmaking.matchmaking_service import MatchmakingService, MatchmakingState


def user(user_id: int, rating: int) -> User:
    return User(user_id, f"Player{user_id}", rating)


@pytest.mark.parametrize("difference", [0, 100, -100])
def test_exact_and_rating_boundaries_match(difference: int) -> None:
    service = MatchmakingService()
    first, second = object(), object()

    assert service.enqueue(first, user(1, 1200)) is None
    match = service.enqueue(second, user(2, 1200 + difference))

    assert match is not None
    assert match.white.client is first
    assert match.black.client is second
    assert service.queued_entries == ()


@pytest.mark.parametrize("difference", [101, -101])
def test_outside_rating_boundaries_remains_queued(difference: int) -> None:
    service = MatchmakingService()

    service.enqueue(object(), user(1, 1200))
    assert service.enqueue(object(), user(2, 1200 + difference)) is None

    assert len(service.queued_entries) == 2


def test_duplicate_play_cancel_and_disconnect_are_idempotent() -> None:
    service = MatchmakingService()
    client = object()

    service.enqueue(client, user(1, 1200))
    service.enqueue(client, user(1, 1200))
    assert len(service.queued_entries) == 1
    assert service.cancel(client)
    assert not service.cancel(client)
    service.disconnect(client)
    assert service.state_for(client) is MatchmakingState.IDLE


def test_same_account_cannot_match_itself_or_be_matched_twice() -> None:
    service = MatchmakingService()
    first, second, third = object(), object(), object()
    service.enqueue(first, user(1, 1200))
    assert service.enqueue(second, user(1, 1200)) is None
    match = service.enqueue(third, user(2, 1200))

    assert match is not None
    assert service.enqueue(first, user(1, 1200)) is None
    assert service.state_for(first) is MatchmakingState.MATCHED


def test_concurrent_requests_create_one_match_without_duplicates() -> None:
    service = MatchmakingService()
    clients = [object(), object()]
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(
            executor.map(
                lambda item: service.enqueue(*item),
                [(clients[0], user(1, 1200)), (clients[1], user(2, 1200))],
            )
        )

    matches = [result for result in results if result is not None]
    assert len(matches) == 1
    assert service.queued_entries == ()
    assert all(
        service.state_for(client) is MatchmakingState.MATCHED
        for client in clients
    )
