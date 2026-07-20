"""Temporary match-started dialog state for the existing OpenCV UI."""

import time

from view.ui.render.overlay_renderer import OverlayRenderer


class MatchStartedDialogController:
    """Shows both player profiles for a short, non-blocking duration."""

    DISPLAY_SECONDS = 4.0

    def __init__(self, overlay_renderer: OverlayRenderer) -> None:
        self._overlay_renderer = overlay_renderer
        self._message: str | None = None
        self._expires_at = 0.0

    def show(self, message: str) -> None:
        """Display a new match summary for the configured duration."""
        self._message = message
        self._expires_at = time.perf_counter() + self.DISPLAY_SECONDS

    def draw(self) -> None:
        """Draw the dialog until its expiration time."""
        if self._message is None:
            return
        if time.perf_counter() >= self._expires_at:
            self._message = None
            return
        self._overlay_renderer.draw_match_started(self._message)
