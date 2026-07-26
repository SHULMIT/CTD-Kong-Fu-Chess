"""Small helpers for consistent application timestamps."""

from datetime import datetime, timezone


def utc_now() -> datetime:
    """Return the current time as a timezone-aware UTC datetime.

    מבצעת את פעולת ``utc`` ``now``."""

    return datetime.now(timezone.utc)
