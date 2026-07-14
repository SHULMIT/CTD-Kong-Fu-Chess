"""Render a short, animated chess game using the existing UI sprites.

Run ``python run_ui_game_demo.py --show`` to watch it, or run it without
arguments to save the individual frames under ``view/ui/assets/preview``.
The script intentionally keeps its state in dictionaries and functions so it
can serve as a lightweight UI integration demo without adding game/UI classes.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np

from view.ui.constants.ui_paths import (
    BACKGROUND_PATH,
    BOARD_PATH,
    DEFAULT_GAME_DEMO_OUTPUT_DIR,
    PIECES_ASSETS_DIR,
)
from view.ui.graphics.img import Img
from view.ui.layout.board_layout import BoardLayout

WINDOW_TITLE = "Kung Fu Chess UI demo"
FRAMES_PER_MOVE = 6


def _write_image(path: Path, image: np.ndarray) -> None:
    """Write an image safely when the project path contains Unicode."""
    path.parent.mkdir(parents=True, exist_ok=True)
    ok, encoded = cv2.imencode(path.suffix or ".png", image)
    if not ok:
        raise ValueError(f"Failed to encode frame: {path}")
    encoded.tofile(str(path))


def _initial_positions() -> dict[tuple[int, int], str]:
    positions: dict[tuple[int, int], str] = {}
    back_rank = ("R", "N", "B", "Q", "K", "B", "N", "R")
    for column, piece_type in enumerate(back_rank):
        positions[(0, column)] = f"{piece_type}B"
        positions[(7, column)] = f"{piece_type}W"
        positions[(1, column)] = "PB"
        positions[(6, column)] = "PW"
    return positions


def _game_moves() -> tuple[tuple[tuple[int, int], tuple[int, int]], ...]:
    """A legal-looking opening with a capture, suitable for a UI animation."""
    return (
        ((6, 4), (4, 4)),  # e2-e4
        ((1, 4), (3, 4)),  # e7-e5
        ((7, 6), (5, 5)),  # Ng1-f3
        ((0, 1), (2, 2)),  # Nb8-c6
        ((7, 5), (4, 2)),  # Bf1-c4
        ((0, 6), (2, 5)),  # Ng8-f6
        ((4, 2), (1, 5)),  # Bc4xf7
        ((0, 4), (1, 5)),  # Ke8xf7
        ((7, 3), (6, 4)),  # Qd1-e2
        ((0, 5), (3, 2)),  # Bf8-c5
    )


def _sprite_frames(
    piece_code: str,
    state: str,
    square_size: int,
    cache: dict[tuple[str, str, int], tuple[Img, ...]],
) -> tuple[Img, ...]:
    key = (piece_code, state, square_size)
    if key not in cache:
        sprites_dir = PIECES_ASSETS_DIR / piece_code / "states" / state / "sprites"
        paths = sorted(sprites_dir.glob("*.png"), key=lambda path: int(path.stem))
        cache[key] = tuple(Img().read(path, (square_size, square_size)) for path in paths)
    return cache[key]


def _draw_piece(
    canvas: Img,
    layout: BoardLayout,
    piece_code: str,
    row: float,
    column: float,
    state: str,
    frame_number: int,
    cache: dict[tuple[str, str, int], tuple[Img, ...]],
) -> None:
    frames = _sprite_frames(piece_code, state, layout.square_size, cache)
    x = int(layout.cells_x + column * layout.square_size)
    y = int(layout.cells_y + row * layout.square_size)
    frames[frame_number % len(frames)].draw_on(canvas, x, y)


def render_game_demo(
    output_dir: Path = DEFAULT_GAME_DEMO_OUTPUT_DIR,
    show_window: bool = False,
    frame_delay_ms: int = 90,
) -> list[Path]:
    """Create a dynamic sequence of frames showing pieces moving on the board."""
    background = Img().read(BACKGROUND_PATH)
    height, width = background.img.shape[:2]
    layout = BoardLayout(window_width=width, window_height=height)
    board = Img().read(BOARD_PATH, (layout.board_size, layout.board_size))
    positions = _initial_positions()
    cache: dict[tuple[str, str, int], tuple[Img, ...]] = {}
    output_paths: list[Path] = []
    frame_index = 0

    if show_window:
        cv2.namedWindow(WINDOW_TITLE, cv2.WINDOW_AUTOSIZE)

    for source, target in _game_moves():
        moving_piece = positions[source]
        static_positions = dict(positions)
        del static_positions[source]
        static_positions.pop(target, None)  # Captured pieces disappear during the move.

        for step in range(FRAMES_PER_MOVE):
            canvas = Img()
            canvas.img = background.img.copy()
            board.draw_on(canvas, layout.board_x, layout.board_y)

            for (row, column), piece_code in static_positions.items():
                _draw_piece(canvas, layout, piece_code, row, column, "idle", frame_index, cache)

            progress = (step + 1) / FRAMES_PER_MOVE
            row = source[0] + (target[0] - source[0]) * progress
            column = source[1] + (target[1] - source[1]) * progress
            _draw_piece(canvas, layout, moving_piece, row, column, "move", step, cache)

            frame_path = output_dir / f"frame_{frame_index:03}.png"
            _write_image(frame_path, canvas.img)
            output_paths.append(frame_path)
            frame_index += 1

            if show_window:
                cv2.imshow(WINDOW_TITLE, Img.fit_to_screen(canvas.img))
                if cv2.waitKey(frame_delay_ms) & 0xFF in (27, ord("q")):
                    cv2.destroyAllWindows()
                    return output_paths

        positions.pop(source)
        positions[target] = moving_piece

    if show_window:
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return output_paths


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render an animated Kung Fu Chess UI demo.")
    parser.add_argument("--show", action="store_true", help="Play the generated frames in a window.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_GAME_DEMO_OUTPUT_DIR)
    parser.add_argument("--frame-delay", type=int, default=90, help="Milliseconds per frame when --show is used.")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    frames = render_game_demo(args.output_dir, args.show, args.frame_delay)
    print(f"Generated {len(frames)} animation frames in: {args.output_dir}")
