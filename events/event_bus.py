"""Deterministic, synchronous publish/subscribe event dispatching."""

from collections.abc import Callable
from typing import TypeVar, cast

from events.event import Event
from events.subscription import Subscription

EventType = TypeVar("EventType", bound=Event)
EventHandler = Callable[[EventType], None]


class EventBus:
    """Manages event subscriptions and dispatches events synchronously.

    מייצגת את רכיב השרת ``EventBus`` ומרכזת את התנהגותו.

    Responsibility: Manages event subscriptions and dispatches events synchronously.

    אחריות: מייצגת את רכיב השרת ``EventBus`` ומרכזת את התנהגותו."""

    def __init__(self) -> None:
        """Initialize the instance and its dependencies.

        מאתחלת את המופע ואת התלויות שלו."""
        self._handlers: dict[
            type[Event],
            list[tuple[Subscription, EventHandler[Event]]],
        ] = {}
        self._owner = object()
        self._next_identifier = 0

    def subscribe(
        self,
        event_type: type[EventType],
        handler: EventHandler[EventType],
    ) -> Subscription:
        """Register a handler for one concrete event type.

                Repeated registration of the same handler for the same event type
                returns the existing subscription instead of adding a duplicate.

        מבצעת את פעולת ``subscribe``."""
        handlers = self._handlers.setdefault(event_type, [])
        existing = self._find_subscription(handlers, handler)
        if existing is not None:
            return existing

        subscription = Subscription(
            _event_type=event_type,
            _identifier=self._next_identifier,
            _owner=self._owner,
        )
        self._next_identifier += 1
        handlers.append((subscription, cast(EventHandler[Event], handler)))
        return subscription

    def publish(self, event: Event) -> None:
        """Call subscribed handlers in registration order.

                A snapshot protects the current dispatch from subscription changes made
                by a handler. Subscriber exceptions intentionally propagate to the
                publisher.

        מבצעת את פעולת ``publish``."""
        handlers = tuple(self._handlers.get(type(event), ()))
        for _, handler in handlers:
            handler(event)

    def unsubscribe(self, subscription: Subscription) -> None:
        """Remove a registration if it belongs to this event bus.

        מבצעת את פעולת ``unsubscribe``."""
        if subscription._owner is not self._owner:
            return

        handlers = self._handlers.get(subscription._event_type)
        if handlers is None:
            return

        remaining = [entry for entry in handlers if entry[0] != subscription]
        if remaining:
            self._handlers[subscription._event_type] = remaining
        else:
            self._handlers.pop(subscription._event_type, None)

    def clear(self) -> None:
        """Remove all subscriptions from this event bus.

        מבצעת את פעולת ``clear``."""
        self._handlers.clear()

    @staticmethod
    def _find_subscription(
        handlers: list[tuple[Subscription, EventHandler[Event]]],
        handler: EventHandler[EventType],
    ) -> Subscription | None:
        """Find and return subscription.

        מאתרת ומחזירה את המינוי."""
        for subscription, registered_handler in handlers:
            if registered_handler == handler:
                return subscription
        return None
        
