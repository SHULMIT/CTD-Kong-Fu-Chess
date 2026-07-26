"""Shared OpenCV colors and lightweight drawing primitives."""

import cv2
import numpy as np


class GamePalette:
    """BGR colors that complement the existing wooden board theme."""

    PANEL = (30, 33, 38)
    PANEL_RAISED = (39, 43, 49)
    BORDER = (67, 72, 80)
    TEXT = (239, 240, 242)
    MUTED_TEXT = (181, 183, 187)
    ACCENT = (82, 138, 181)
    ERROR = (116, 126, 211)
    SUCCESS = (143, 184, 132)
    SHADOW = (10, 11, 13)


def draw_status_icon(
    image: np.ndarray,
    center: tuple[int, int],
    color: tuple[int, int, int],
    symbol: str,
    radius: int = 15,
) -> None:
    """Draw a compact dependency-free icon for a notification."""
    cv2.circle(image, center, radius, color, -1, cv2.LINE_AA)
    if symbol == "check":
        x, y = center
        cv2.line(
            image,
            (x - 7, y),
            (x - 2, y + 6),
            GamePalette.PANEL,
            2,
            cv2.LINE_AA,
        )
        cv2.line(
            image,
            (x - 2, y + 6),
            (x + 8, y - 7),
            GamePalette.PANEL,
            2,
            cv2.LINE_AA,
        )
        return
    font_scale = 0.55
    thickness = 2
    (text_width, text_height), _ = cv2.getTextSize(
        symbol, cv2.FONT_HERSHEY_DUPLEX, font_scale, thickness
    )
    cv2.putText(
        image,
        symbol,
        (center[0] - text_width // 2, center[1] + text_height // 2),
        cv2.FONT_HERSHEY_DUPLEX,
        font_scale,
        GamePalette.PANEL,
        thickness,
        cv2.LINE_AA,
    )


def draw_rounded_panel(
    image: np.ndarray,
    left: int,
    top: int,
    width: int,
    height: int,
    *,
    radius: int = 18,
    opacity: float = 0.94,
    color: tuple[int, int, int] = GamePalette.PANEL,
    border_color: tuple[int, int, int] = GamePalette.BORDER,
) -> None:
    """Draw a softly rounded, translucent panel with a subtle border."""
    if width <= 0 or height <= 0:
        return
    radius = min(radius, width // 2, height // 2)
    overlay = image.copy()
    _rounded_rectangle(overlay, left + 3, top + 5, width, height, radius, GamePalette.SHADOW)
    cv2.addWeighted(overlay, 0.22, image, 0.78, 0, image)

    overlay = image.copy()
    _rounded_rectangle(overlay, left, top, width, height, radius, color)
    cv2.addWeighted(overlay, opacity, image, 1.0 - opacity, 0, image)
    _rounded_outline(image, left, top, width, height, radius, border_color)


def _rounded_rectangle(
    image: np.ndarray,
    left: int,
    top: int,
    width: int,
    height: int,
    radius: int,
    color: tuple[int, int, int],
) -> None:
    right, bottom = left + width, top + height
    cv2.rectangle(image, (left + radius, top), (right - radius, bottom), color, -1)
    cv2.rectangle(image, (left, top + radius), (right, bottom - radius), color, -1)
    for center in (
        (left + radius, top + radius),
        (right - radius, top + radius),
        (left + radius, bottom - radius),
        (right - radius, bottom - radius),
    ):
        cv2.circle(image, center, radius, color, -1, cv2.LINE_AA)


def _rounded_outline(
    image: np.ndarray,
    left: int,
    top: int,
    width: int,
    height: int,
    radius: int,
    color: tuple[int, int, int],
) -> None:
    right, bottom = left + width, top + height
    cv2.line(image, (left + radius, top), (right - radius, top), color, 1, cv2.LINE_AA)
    cv2.line(image, (left + radius, bottom), (right - radius, bottom), color, 1, cv2.LINE_AA)
    cv2.line(image, (left, top + radius), (left, bottom - radius), color, 1, cv2.LINE_AA)
    cv2.line(image, (right, top + radius), (right, bottom - radius), color, 1, cv2.LINE_AA)
    for center, start, end in (
        ((left + radius, top + radius), 180, 270),
        ((right - radius, top + radius), 270, 360),
        ((right - radius, bottom - radius), 0, 90),
        ((left + radius, bottom - radius), 90, 180),
    ):
        cv2.ellipse(image, center, (radius, radius), 0, start, end, color, 1, cv2.LINE_AA)
