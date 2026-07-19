"""Tests for player activity time presentation."""

from datetime import datetime

from view.ui.render.player_activity_renderer import PlayerActivityRenderer


def test_formats_action_time_with_hours_minutes_seconds_and_milliseconds() -> None:
    occurred_at = datetime(2026, 7, 19, 14, 5, 9, 321_000)

    assert PlayerActivityRenderer._format_time(occurred_at) == "14:05:09.321"
