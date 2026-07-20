"""Tests for player activity time presentation."""

from datetime import datetime, timezone

from view.ui.render.player_activity_renderer import PlayerActivityRenderer


def test_formats_utc_action_time_as_local_time_with_milliseconds() -> None:
    occurred_at = datetime(
        2026,
        7,
        19,
        14,
        5,
        9,
        321_000,
        tzinfo=timezone.utc,
    )
    expected = occurred_at.astimezone().strftime("%H:%M:%S.%f")[:-3]

    assert PlayerActivityRenderer._format_time(occurred_at) == expected
