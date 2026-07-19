"""Tests for temporary UI status messages."""

from unittest.mock import Mock, patch

from view.ui.feedback.status_message_controller import StatusMessageController


def test_status_message_is_drawn_before_expiration() -> None:
    overlay_renderer = Mock()
    controller = StatusMessageController(overlay_renderer)

    with patch(
        "view.ui.feedback.status_message_controller.time.perf_counter",
        side_effect=[10.0, 11.9],
    ):
        controller.show("Illegal move")
        controller.draw()

    overlay_renderer.draw_status_message.assert_called_once_with("Illegal move")


def test_status_message_is_not_drawn_after_two_seconds() -> None:
    overlay_renderer = Mock()
    controller = StatusMessageController(overlay_renderer)

    with patch(
        "view.ui.feedback.status_message_controller.time.perf_counter",
        side_effect=[10.0, 12.0],
    ):
        controller.show("Illegal move")
        controller.draw()

    overlay_renderer.draw_status_message.assert_not_called()
