"""Immutable registration handle returned by the event bus."""

from dataclasses import dataclass

from events.event import Event


@dataclass(frozen=True)
class Subscription:
    """Identifies one handler registration for safe unsubscription.

    מייצגת את רכיב השרת ``Subscription`` ומרכזת את התנהגותו.

    Responsibility: Identifies one handler registration for safe unsubscription.

    אחריות: מייצגת את רכיב השרת ``Subscription`` ומרכזת את התנהגותו."""

    _event_type: type[Event]
    _identifier: int
    _owner: object
