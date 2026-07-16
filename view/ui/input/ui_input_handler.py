"""
ui_input_handler.py

Handles mouse events from the game window.

Responsibilities:
    - Listen for mouse clicks.
    - Convert display coordinates to board positions.
    - Forward clicks to the controller.
"""

import cv2

from controller.controller import Controller
from view.ui.input.coordinate_scaler import CoordinateScaler
from view.ui.layout.board_layout import BoardLayout


class UiInputHandler:

    def __init__(
        self,
        layout: BoardLayout,
        controller: Controller,
        scaler: CoordinateScaler,
    ):
        self._layout = layout
        self._controller = controller
        self._scaler = scaler

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

        if event not in (
            cv2.EVENT_LBUTTONDOWN,
            cv2.EVENT_RBUTTONDOWN,
        ):
            return

        # Convert from display pixels to full-canvas pixels.
        canvas_x, canvas_y = self._scaler.to_canvas(x, y)

        if not self._layout.is_inside_board(canvas_x, canvas_y):
            return

        position = self._layout.pixel_to_cell(canvas_x, canvas_y)

        if event == cv2.EVENT_RBUTTONDOWN:
            self._controller.jump_at(position)
            return

        self._controller.handle_position(position)
