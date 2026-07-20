"""Focused tests for synchronous event dispatching."""

from dataclasses import dataclass

from events.event import Event
from events.event_bus import EventBus


@dataclass(frozen=True)
class ExampleEvent(Event):
    value: int


@dataclass(frozen=True)
class OtherEvent(Event):
    value: int


def test_subscribed_handler_receives_published_event() -> None:
    event_bus = EventBus()
    received: list[ExampleEvent] = []
    event = ExampleEvent(7)

    event_bus.subscribe(ExampleEvent, received.append)
    event_bus.publish(event)

    assert received == [event]


def test_multiple_handlers_receive_the_same_event_in_subscription_order() -> None:
    event_bus = EventBus()
    calls: list[tuple[str, ExampleEvent]] = []
    event = ExampleEvent(3)

    event_bus.subscribe(ExampleEvent, lambda item: calls.append(("first", item)))
    event_bus.subscribe(ExampleEvent, lambda item: calls.append(("second", item)))
    event_bus.publish(event)

    assert calls == [("first", event), ("second", event)]


def test_unrelated_event_type_does_not_trigger_handler() -> None:
    event_bus = EventBus()
    received: list[ExampleEvent] = []
    event_bus.subscribe(ExampleEvent, received.append)

    event_bus.publish(OtherEvent(1))

    assert received == []


def test_unsubscribe_removes_handler() -> None:
    event_bus = EventBus()
    received: list[ExampleEvent] = []
    subscription = event_bus.subscribe(ExampleEvent, received.append)

    event_bus.unsubscribe(subscription)
    event_bus.publish(ExampleEvent(4))

    assert received == []


def test_event_bus_instances_are_independent() -> None:
    first_bus = EventBus()
    second_bus = EventBus()
    received: list[ExampleEvent] = []
    first_bus.subscribe(ExampleEvent, received.append)

    second_bus.publish(ExampleEvent(5))

    assert received == []


def test_subscription_changes_do_not_modify_current_dispatch() -> None:
    event_bus = EventBus()
    calls: list[str] = []

    def subscribe_late(_: ExampleEvent) -> None:
        calls.append("first")
        event_bus.subscribe(ExampleEvent, lambda event: calls.append("late"))

    event_bus.subscribe(ExampleEvent, subscribe_late)
    event_bus.subscribe(ExampleEvent, lambda event: calls.append("second"))

    event_bus.publish(ExampleEvent(1))

    assert calls == ["first", "second"]
