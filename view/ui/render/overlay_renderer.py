"""
overlay_renderer.py

Draws overlays on top of the game board.

Responsibilities:
    - Highlight the selected piece with a glowing blue border.
    - Show legal move destinations as semi-transparent dots.
    - Draw the game-over screen.
"""

import cv2
import numpy as np

from model.position import Position

from view.ui.layout.board_layout import BoardLayout
from view.ui.window.game_canvas import GameCanvas


class OverlayRenderer:
    """
    Draws visual overlays above the board.
    """

    def __init__(
        self,
        canvas: GameCanvas,
        layout: BoardLayout,
    ):
        self._canvas = canvas
        self._layout = layout

    def draw_selected(
        self,
        position: Position | None,
    ) -> None:
        """
        Draws a glowing blue border around the selected cell.
        """

        if position is None:
            return

        img = self._canvas.canvas.img
        x, y = self._layout.cell_to_pixel(position)
        s = self._layout.square_size
        thickness = max(3, s // 20)

        # Outer glow — multiple semi-transparent rectangles expanding outward
        for i in range(4, 0, -1):
            alpha = 0.15 * i
            glow_color = (255, 180, 0)  # bright blue-cyan in BGR
            overlay = img.copy()
            pad = i * (thickness // 2 + 1)
            cv2.rectangle(
                overlay,
                (x - pad, y - pad),
                (x + s + pad, y + s + pad),
                glow_color,
                thickness,
            )
            cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)

        # Solid bright border on top
        cv2.rectangle(
            img,
            (x, y),
            (x + s, y + s),
            (255, 200, 0),   # bright cyan-blue
            thickness,
        )

    def draw_legal_moves(
        self,
        positions: set[Position],
    ) -> None:
        """
        Draws semi-transparent dots on all legal move destinations.

        Empty squares get a small filled circle in the centre.
        Squares occupied by an enemy piece get a ring overlay.
        """

        if not positions:
            return

        img = self._canvas.canvas.img
        s = self._layout.square_size
        dot_radius = max(6, s // 8)
        ring_thickness = max(4, s // 14)

        for pos in positions:
            x, y = self._layout.cell_to_pixel(pos)
            cx = x + s // 2
            cy = y + s // 2

            overlay = img.copy()
            cv2.circle(overlay, (cx, cy), dot_radius, (0, 200, 0), -1)
            cv2.addWeighted(overlay, 0.55, img, 0.45, 0, img)

    def draw_game_over(self, winner: str) -> None:
        """
        Draws a semi-transparent dark overlay with a GAME OVER message.
        """

        img = self._canvas.canvas.img
        h, w = img.shape[:2]

        overlay = img.copy()
        cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.55, img, 0.45, 0, img)

        scale = w / 1000.0
        thickness = max(2, int(scale * 3))

        def _centered_text(text: str, y_frac: float, color: tuple) -> None:
            font = cv2.FONT_HERSHEY_DUPLEX
            (tw, _th), _ = cv2.getTextSize(text, font, scale * 2.5, thickness)
            tx = (w - tw) // 2
            ty = int(h * y_frac)
            cv2.putText(img, text, (tx + 3, ty + 3), font,
                        scale * 2.5, (0, 0, 0), thickness + 2, cv2.LINE_AA)
            cv2.putText(img, text, (tx, ty), font,
                        scale * 2.5, color, thickness, cv2.LINE_AA)

        _centered_text("GAME OVER", 0.42, (255, 255, 255))
        _centered_text(winner,      0.55, (0, 215, 255))

    def draw_status_message(self, message: str) -> None:
        """Draw a short user-feedback message below the board."""
        image = self._canvas.canvas.img
        center_x = self._layout.board_x + self._layout.board_size // 2
        text_y = self._layout.board_y + self._layout.board_size + 30
        font = cv2.FONT_HERSHEY_DUPLEX
        scale = 0.7
        thickness = 2
        (text_width, _), _ = cv2.getTextSize(message, font, scale, thickness)
        cv2.putText(
            image,
            message,
            (center_x - text_width // 2, text_y),
            font,
            scale,
            (0, 0, 255),
            thickness,
            cv2.LINE_AA,
        )
