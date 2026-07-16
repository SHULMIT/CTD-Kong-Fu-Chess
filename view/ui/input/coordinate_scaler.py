"""
coordinate_scaler.py

Converts between displayed (scaled-down) pixel coordinates and
full-canvas pixel coordinates.

Responsibility:
    - One place that knows how to undo the fit-to-screen scaling
      so that every other class can work in full-resolution coordinates.
"""

from view.ui.window.game_canvas import GameCanvas


class CoordinateScaler:
    """
    Converts display pixels to full-canvas pixels.

    The game canvas is rendered at a reduced size to fit the screen.
    Mouse events from OpenCV arrive in display pixels.
    This class converts them back to the original canvas resolution
    so the layout calculations stay correct.
    """

    def __init__(self, canvas: GameCanvas) -> None:
        self._canvas = canvas

    def to_canvas(self, display_x: int, display_y: int) -> tuple[int, int]:
        """
        Converts displayed pixel coordinates to full-canvas pixel coordinates.
        """
        scale = self._canvas.display_scale
        if scale <= 0:
            return display_x, display_y
        return int(display_x / scale), int(display_y / scale)
