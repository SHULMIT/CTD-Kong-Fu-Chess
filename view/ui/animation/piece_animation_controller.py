"""
piece_animation_controller.py

Manages the per-piece animation state, frame index, and timing.

Responsibilities:
    - Track which AnimationState each piece is currently displaying.
    - Detect when a piece's PieceState changes and reset the frame timer.
    - Compute the correct frame index based on elapsed time and animation fps.
    - Provide the current frame index for any piece.

This class does NOT load images, draw to the canvas, or know about pixels.
"""

import time

from model.piece import Piece, PieceState
from view.ui.animation.animation_state import AnimationState
from view.ui.animation.animation_state_resolver import AnimationStateResolver
from view.ui.animation.sprite_animation import SpriteAnimation


class PieceAnimationController:
    """
    Tracks animation state and frame timing for every chess piece.

    Each piece is identified by its unique id.
    When a piece transitions to a new PieceState, the animation resets
    to frame 0 so the new animation always starts from the beginning.
    """

    def __init__(self) -> None:
        # Maps piece_id → last known AnimationState
        self._current_anim_state: dict[int, AnimationState] = {}
        # Maps piece_id → wall-clock time when the current animation started
        self._anim_start_time: dict[int, float] = {}

    def get_frame_index(
        self,
        piece: Piece,
        animation: SpriteAnimation,
    ) -> int:
        """
        Returns the current frame index for the given piece and animation.

        If the piece's PieceState has changed since the last call, the
        animation timer resets to 0 so the new animation starts cleanly.

        Parameters
        ----------
        piece : Piece
            The piece being rendered.
        animation : SpriteAnimation
            The animation that is about to be drawn (already resolved to
            the correct state by the caller).

        Returns
        -------
        int
            Index into animation.frames for the current frame.
        """
        resolved_state = AnimationStateResolver.resolve(piece.state)
        now = time.perf_counter()

        # Reset timer whenever the animation state changes.
        previous_state = self._current_anim_state.get(piece.id)
        if previous_state != resolved_state:
            self._current_anim_state[piece.id] = resolved_state
            self._anim_start_time[piece.id] = now

        elapsed = now - self._anim_start_time.get(piece.id, now)
        frame_count = len(animation.frames)
        fps = animation.fps if animation.fps > 0 else 8

        if animation.loop:
            return int(elapsed * fps) % frame_count
        else:
            # Non-looping animation clamps at the last frame.
            return min(int(elapsed * fps), frame_count - 1)

    def reset(self, piece: Piece) -> None:
        """Clears all animation tracking for a piece (e.g. on capture)."""
        self._current_anim_state.pop(piece.id, None)
        self._anim_start_time.pop(piece.id, None)

    def clear(self) -> None:
        """Removes all tracked animation states."""
        self._current_anim_state.clear()
        self._anim_start_time.clear()
