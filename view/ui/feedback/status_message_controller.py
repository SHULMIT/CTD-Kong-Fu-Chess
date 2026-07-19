"""Owns temporary user-feedback message state for the game scene."""

import time

from view.ui.render.overlay_renderer import OverlayRenderer


class StatusMessageController:
    """Displays a status message until its configured expiration time."""

    DEFAULT_DURATION_SECONDS = 2.0

    def __init__(
        self,
        overlay_renderer: OverlayRenderer,
        duration_seconds: float = DEFAULT_DURATION_SECONDS,
    ) -> None:
        self._overlay_renderer = overlay_renderer
        self._duration_seconds = duration_seconds
        self._message: str | None = None
        self._expires_at = 0.0

    def show(self, message: str) -> None:
        """Show a message for the configured duration."""
        self._message = message
        self._expires_at = time.perf_counter() + self._duration_seconds

    def draw(self) -> None:
        """Draw the active message, clearing it after expiration."""
        if self._message is None:
            return
        if time.perf_counter() >= self._expires_at:
            self._message = None
            return
        self._overlay_renderer.draw_status_message(self._message)
