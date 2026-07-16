"""Quick UI preview runner for the current board/background assets."""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np

from view.ui.graphics.img import Img
from view.ui.layout.board_layout import BoardLayout
from view.ui.render.board_renderer import BoardRenderer
from view.ui.window.game_canvas import GameCanvas
from view.ui.constants.ui_paths import (
    BACKGROUND_PATH,
    BOARD_PATH,
    DEFAULT_PREVIEW_OUTPUT_PATH,
)

DEFAULT_OUTPUT_PATH = DEFAULT_PREVIEW_OUTPUT_PATH
DEFAULT_WINDOW_WIDTH = 1200
DEFAULT_WINDOW_HEIGHT = 900


def _write_image(path: Path, image: np.ndarray) -> None:
    """
    Writes an image in a Unicode-safe way for Windows paths.
    """

    path.parent.mkdir(parents=True, exist_ok=True)
    ext = path.suffix or ".jpg"
    ok, encoded = cv2.imencode(ext, image)

    if not ok:
        raise ValueError(f"Failed to encode image for: {path}")

    encoded.tofile(str(path))


def _create_placeholder_background(path: Path, width: int, height: int) -> None:
    # A soft gradient background to make board preview visible.
    canvas = np.zeros((height, width, 3), dtype=np.uint8)
    for row in range(height):
        blend = row / max(1, height - 1)
        canvas[row, :, 0] = int(30 + 25 * blend)
        canvas[row, :, 1] = int(40 + 35 * blend)
        canvas[row, :, 2] = int(55 + 45 * blend)

    _write_image(path, canvas)


def _create_placeholder_board(path: Path, board_size: int) -> None:
    board = np.zeros((board_size, board_size, 3), dtype=np.uint8)
    square = board_size // 8

    light = (240, 217, 181)
    dark = (181, 136, 99)

    for row in range(8):
        for col in range(8):
            color = light if (row + col) % 2 == 0 else dark
            y1 = row * square
            y2 = (row + 1) * square
            x1 = col * square
            x2 = (col + 1) * square
            board[y1:y2, x1:x2] = color

    _write_image(path, board)


def _ensure_assets(window_width: int, window_height: int) -> None:
    layout = BoardLayout(window_width=window_width, window_height=window_height)

    if not BACKGROUND_PATH.exists():
        _create_placeholder_background(BACKGROUND_PATH, window_width, window_height)

    if not BOARD_PATH.exists():
        _create_placeholder_board(BOARD_PATH, layout.board_size)


def _draw_board_with_fallback(canvas: GameCanvas, layout: BoardLayout) -> None:
    try:
        board_img = Img().read(
            str(BOARD_PATH),
            size=(layout.board_size, layout.board_size),
        )
        renderer = BoardRenderer(
            canvas=canvas,
            layout=layout,
            board=board_img,
        )
        renderer.draw()

    except (ValueError, FileNotFoundError):
        # If the source board is too large for the current background,
        # resize it and draw directly as a safe fallback.
        resized_board = Img().read(
            str(BOARD_PATH),
            size=(layout.board_size, layout.board_size),
        )
        resized_board.draw_on(canvas.canvas, layout.board_x, layout.board_y)


def _save_preview(canvas: GameCanvas, output_path: Path) -> None:
    _write_image(output_path, canvas.canvas.img)


def main(
    show_window: bool = False,
    output_path: Path = DEFAULT_OUTPUT_PATH,
) -> Path:
    _ensure_assets(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)

    game_canvas = GameCanvas(background_source=str(BACKGROUND_PATH))
    height, width = game_canvas.canvas.img.shape[:2]
    layout = BoardLayout(window_width=width, window_height=height)
    _draw_board_with_fallback(game_canvas, layout)
    _save_preview(game_canvas, output_path)

    if show_window:
        print("Opening UI preview window. Close it to finish.")
        game_canvas.show()
    else:
        print(f"UI preview saved to: {output_path}")

    return output_path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a UI preview image.")
    parser.add_argument(
        "--show",
        action="store_true",
        help="Open the preview in a window after rendering.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Path to save the rendered preview image.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    main(show_window=args.show, output_path=args.output)
