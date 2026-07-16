import ctypes

import cv2
import numpy as np

from view.ui.graphics.img import Img
from typing import Callable


class GameCanvas:
    """
    game_canvas.py

    Represents the main drawing surface of the game.

    Responsibilities:
        - Store the game canvas.
        - Reset the canvas to the background at the start of each frame.
        - Present the current frame scaled to fit the screen.
        - Track the display scale so mouse coordinates can be converted back
          to canvas coordinates.
        - Handle window events.
    """

    WINDOW_NAME = "Kung Fu Chess"

    def __init__(
        self,
        background_source: str | Img,
    ):
        if isinstance(background_source, Img):
            self._background_img = background_source.img.copy()
        else:
            self._background_img = Img().read(background_source).img.copy()

        # Working canvas — gets reset to background at the start of every frame.
        self._canvas = Img()
        self._canvas.img = self._background_img.copy()

        # Scale factor: canvas_pixels / display_pixels.
        # Updated every time present() is called so mouse events can be
        # converted back to full-resolution coordinates.
        self._display_scale: float = 1.0

        self._window_created = False

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def canvas(self) -> Img:
        """Returns the working canvas that renderers draw onto."""
        return self._canvas

    @property
    def width(self) -> int:
        return self._background_img.shape[1]

    @property
    def height(self) -> int:
        return self._background_img.shape[0]

    @property
    def display_scale(self) -> float:
        """
        Ratio of full-canvas pixels to displayed pixels.
        Use this to convert a mouse click coordinate:
            canvas_x = display_x / display_scale
        """
        return self._display_scale

    def to_canvas_coords(self, display_x: int, display_y: int) -> tuple[int, int]:
        """
        Converts displayed (scaled-down) pixel coordinates to
        full-canvas pixel coordinates.

        Responsibility: GameCanvas owns the scale, so it owns this conversion.
        """
        scale = self._display_scale if self._display_scale > 0 else 1.0
        return int(display_x / scale), int(display_y / scale)

    # ------------------------------------------------------------------
    # Frame lifecycle
    # ------------------------------------------------------------------

    def reset(self) -> None:
        """
        Resets the working canvas to the original background.
        Call this at the beginning of every draw() cycle so that
        pieces and overlays from the previous frame are erased.
        """
        self._canvas.img = self._background_img.copy()

    def _ensure_window(self) -> None:
        """Creates the OpenCV window once."""
        if not self._window_created:
            cv2.namedWindow(self.WINDOW_NAME, cv2.WINDOW_KEEPRATIO)
            self._window_created = True

    def present(self) -> None:
        """
        Scales the current canvas to fit the screen and displays it.
        Also updates display_scale so mouse coordinates stay accurate.
        """
        self._ensure_window()

        # Compute scale
        try:
            screen_w = ctypes.windll.user32.GetSystemMetrics(0)
            screen_h = ctypes.windll.user32.GetSystemMetrics(1)
        except (AttributeError, OSError):
            screen_w, screen_h = 1280, 720

        max_w = int(screen_w * 0.85)
        max_h = int(screen_h * 0.85)
        h, w = self._canvas.img.shape[:2]
        scale = min(max_w / w, max_h / h, 1.0)
        self._display_scale = scale

        if scale < 1.0:
            frame = cv2.resize(
                self._canvas.img,
                (int(w * scale), int(h * scale)),
                interpolation=cv2.INTER_AREA,
            )
        else:
            frame = self._canvas.img

        cv2.imshow(self.WINDOW_NAME, frame)

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def poll_events(self) -> int:
        """
        Processes window events and keyboard input.
        Returns the key code (or -1 if no key was pressed).
        """
        return cv2.waitKey(1)

    def is_open(self) -> bool:
        """Returns whether the game window is still open."""
        try:
            visible = cv2.getWindowProperty(
                self.WINDOW_NAME, cv2.WND_PROP_VISIBLE
            )
            autosize = cv2.getWindowProperty(
                self.WINDOW_NAME, cv2.WND_PROP_AUTOSIZE
            )
            return visible >= 0 and autosize >= 0
        except cv2.error:
            return False

    def close(self) -> None:
        """Closes the game window."""
        try:
            cv2.destroyWindow(self.WINDOW_NAME)
        except cv2.error:
            pass
        cv2.waitKey(1)

    def set_mouse_callback(
        self,
        callback: Callable,
    ) -> None:
        """Registers the mouse callback on the window."""
        cv2.setMouseCallback(self.WINDOW_NAME, callback)
