"""Regression tests for login window request and close lifecycle."""

import queue
from unittest.mock import Mock

from view.auth.login_window import LoginWindow


def test_worker_only_queues_response_without_touching_tk() -> None:
    window = LoginWindow.__new__(LoginWindow)
    window._response_queue = queue.Queue()

    window._perform_request(
        lambda username, password: {
            "type": "login_success",
            "username": username,
        },
        "Player_1",
        "password123",
    )

    assert window._response_queue.get_nowait() == {
        "type": "login_success",
        "username": "Player_1",
    }


def test_close_is_idempotent_while_request_is_in_progress() -> None:
    window = LoginWindow.__new__(LoginWindow)
    window._closed = False
    window._request_in_progress = True
    window._root = Mock()

    window._close()
    window._close()

    assert window._closed
    window._root.destroy.assert_called_once_with()
