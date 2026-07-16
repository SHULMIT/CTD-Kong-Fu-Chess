"""
motion_interpolator.py

Calculates the sub-cell pixel position of a moving piece.

Responsibility:
    - Given a Motion and a BoardLayout, return the exact (x, y) pixel
      coordinates that represent the piece's current visual position
      smoothly interpolated between its source and target cells.
"""

from realtime.motion import Motion
from view.ui.layout.board_layout import BoardLayout


class MotionInterpolator:
    """
    Converts a Motion's elapsed time into a smooth pixel position.

    The motion engine moves pieces cell-by-cell on the logical board.
    This class reads elapsed_time / duration to compute a fractional
    progress value and linearly interpolates between the source and
    target pixel coordinates — so the piece glides across the board
    instead of jumping from square to square.
    """

    def __init__(self, layout: BoardLayout) -> None:
        self._layout = layout

    def get_pixel_position(self, motion: Motion) -> tuple[int, int]:
        """
        Returns the interpolated (x, y) pixel position for a moving piece.

        Parameters
        ----------
        motion : Motion
            The active motion object for the piece.

        Returns
        -------
        tuple[int, int]
            Pixel coordinates (x, y) of the top-left corner of the piece
            sprite, ready to pass directly to frame.draw_on().
        """

        duration = motion.duration
        elapsed = motion.elapsed_time

        # Clamp progress to [0.0, 1.0] so rounding never overshoots.
        progress = max(0.0, min(1.0, elapsed / duration if duration > 0 else 1.0))

        src_x, src_y = self._layout.cell_to_pixel(motion.source)
        tgt_x, tgt_y = self._layout.cell_to_pixel(motion.target)

        x = int(src_x + (tgt_x - src_x) * progress)
        y = int(src_y + (tgt_y - src_y) * progress)

        return x, y
