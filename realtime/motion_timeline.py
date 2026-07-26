"""
Provides simulation timeline utilities for active motions.
"""

from realtime.airborne_manager import AirborneManager
from realtime.motion import Motion


class MotionTimeline:
    """Owns simulation clock and event delta calculations.

        This class is intentionally focused on time slicing only.
        It does not resolve collisions or board state transitions.

    מייצגת את רכיב השרת ``MotionTimeline`` ומרכזת את התנהגותו.

    Responsibility: Owns simulation clock and event delta calculations.

    אחריות: מייצגת את רכיב השרת ``MotionTimeline`` ומרכזת את התנהגותו."""

    def __init__(self):
        """Initialize the instance and its dependencies.

        מאתחלת את המופע ואת התלויות שלו."""
        self._clock_milliseconds = 0

    @property
    def current_time(self) -> int:
        """Returns current simulation time.

        מבצעת את פעולת ``current`` הזמן."""

        return self._clock_milliseconds

    def next_event_delta(
        self,
        remaining_time: int,
        motions: list[Motion],
        airborne_manager: AirborneManager,
    ) -> int:
        """Returns the time slice until the next meaningful event.

        מבצעת את פעולת ``next`` אירוע ``delta``."""

        next_event_time = remaining_time

        for motion in motions:
            until_next_step = motion.milliseconds_until_next_step()
            if until_next_step is None:
                continue
            next_event_time = min(next_event_time, until_next_step)

        airborne_delta = airborne_manager.time_until_next_landing()
        if airborne_delta is not None:
            next_event_time = min(next_event_time, airborne_delta)

        # Keep the loop progressing even if callers pass odd values.
        return max(0, next_event_time)

    def advance(
        self,
        motions: list[Motion],
        airborne_manager: AirborneManager,
        milliseconds: int,
    ) -> None:
        """Applies a time slice to motions, airborne timers, and clock.

        מבצעת את פעולת ``advance``."""

        for motion in motions:
            motion.advance_time(milliseconds)

        airborne_manager.advance_time(milliseconds)
        self._clock_milliseconds += milliseconds