"""
ui_input_handler.py

Handles mouse events from the game window.

Responsibilities:
    - Listen for mouse clicks.
    - Convert display coordinates to board positions.
    - Forward clicks to the controller.
"""

import cv2
import time
from typing import Callable

from controller.controller import Controller
from errors.user_input_errors import (
    ClickOutsideBoardError,
    IllegalPieceMoveError,
    UserInputError,
)
from view.ui.input.coordinate_scaler import CoordinateScaler
from view.ui.layout.board_layout import BoardLayout


class UiInputHandler:

    DOUBLE_CLICK_INTERVAL_SECONDS = 0.25

    def __init__(
        self,
        layout: BoardLayout,
        controller: Controller,
        scaler: CoordinateScaler,
        report_user_error: Callable[[str], None],
    ):
        self._layout = layout
        self._controller = controller
        self._scaler = scaler
        self._report_user_error = report_user_error
        self._pending_position = None
        self._pending_click_time = 0.0

    def handle_mouse(
        self,
        event: int,
        x: int,
        y: int,
        flags: int,
        param,
    ) -> None:
        """
        Handles a mouse click event.
        """

        if event not in (cv2.EVENT_LBUTTONDOWN, cv2.EVENT_LBUTTONDBLCLK,
                         cv2.EVENT_RBUTTONDOWN):
            return

        # Convert from display pixels to full-canvas pixels.
        canvas_x, canvas_y = self._scaler.to_canvas(x, y)

        if not self._layout.is_inside_board(canvas_x, canvas_y):
            self._report_user_error(
                str(ClickOutsideBoardError()).replace("_", " ")
            )
            return

        position = self._layout.pixel_to_cell(canvas_x, canvas_y)

        if event == cv2.EVENT_LBUTTONDOWN:
            self._queue_normal_click(position)
        elif event == cv2.EVENT_LBUTTONDBLCLK:
            self._handle_double_click(position)
        else:
            self._perform_jump(position)

    def update(self) -> None:
        """Dispatch a pending single click after the double-click interval."""
        if self._pending_position is None:
            return
        if time.perf_counter() - self._pending_click_time < self.DOUBLE_CLICK_INTERVAL_SECONDS:
            return

        position = self._pending_position
        self._pending_position = None
        self._perform_normal_click(position)

    def _queue_normal_click(self, position) -> None:
        """Delay a normal click so a following double-click can replace it."""
        if self._pending_position is not None and position != self._pending_position:
            self._perform_normal_click(self._pending_position)
        self._pending_position = position
        self._pending_click_time = time.perf_counter()

    def _handle_double_click(self, position) -> None:
        """Cancel the pending click and make the UI jump request."""
        self._pending_position = None
        self._perform_jump(position)

    def _perform_normal_click(self, position) -> None:
        self._run_user_action(self._controller.handle_position, position)

    def _perform_jump(self, position) -> None:
        self._run_user_action(self._controller.jump_at, position)

    def _run_user_action(self, action: Callable, position) -> None:
        try:
            action(position)
        except UserInputError as error:
            if isinstance(error, IllegalPieceMoveError):
                self._report_user_error("Illegal move")
                return
            self._report_user_error(str(error).replace("_", " "))
