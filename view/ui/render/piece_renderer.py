"""
piece_renderer.py

Renders chess pieces on the game canvas.

Responsibilities:
    - Resolve the correct sprite for each piece based on its PieceState.
    - Delegate frame index calculation to PieceAnimationController.
    - Use MotionInterpolator for smooth sub-cell positioning of moving pieces.
    - Draw the correct animation frame at the correct pixel position.
"""

from math import pi, sin

from config.constants import JUMP_DURATION_MILLISECONDS
from model.piece import Piece, PieceState

from realtime.motion import Motion
from view.ui.animation.animation_repository import AnimationRepository
from view.ui.animation.animation_state import AnimationState
from view.ui.animation.animation_state_resolver import AnimationStateResolver
from view.ui.animation.piece_animation_controller import PieceAnimationController
from view.ui.animation.piece_code_resolver import PieceCodeResolver
from view.ui.layout.board_layout import BoardLayout
from view.ui.layout.motion_interpolator import MotionInterpolator
from view.ui.window.game_canvas import GameCanvas


class PieceRenderer:
    """
    Draws chess pieces on the game canvas one frame at a time.
    """

    def __init__(
        self,
        canvas: GameCanvas,
        layout: BoardLayout,
        repository: AnimationRepository,
    ) -> None:
        self._canvas = canvas
        self._layout = layout
        self._repository = repository
        self._interpolator = MotionInterpolator(layout)
        self._anim_controller = PieceAnimationController()

    def draw(
        self,
        piece: Piece,
        active_motions: tuple[Motion, ...] | None = None,
    ) -> None:
        """
        Draws a single chess piece at its current visual position.

        Parameters
        ----------
        piece : Piece
            The piece to draw.
        active_motions : tuple[Motion, ...] | None
            Immutable snapshot of active motions from the game engine.
            Used to compute sub-cell interpolated position for moving pieces.
        """

        # Captured pieces are removed from the board — skip silently.
        if piece.state == PieceState.CAPTURED:
            self._anim_controller.reset(piece)
            return

        piece_code = PieceCodeResolver.resolve(piece)
        anim_state = AnimationStateResolver.resolve(piece.state)

        # Load animation for the resolved state; fall back to IDLE if the
        # sprite folder for this state does not exist yet.
        try:
            animation = self._repository.get(
                piece_code=piece_code,
                state=anim_state,
                size=(self._layout.square_size, self._layout.square_size),
            )
        except (FileNotFoundError, OSError):
            animation = self._repository.get(
                piece_code=piece_code,
                state=AnimationState.IDLE,
                size=(self._layout.square_size, self._layout.square_size),
            )

        # PieceAnimationController tracks state changes and resets the timer
        # automatically when PieceState transitions (e.g. IDLE → MOVING).
        frame_index = self._anim_controller.get_frame_index(piece, animation)
        frame = animation.frames[frame_index]

        # Moving pieces are drawn at their interpolated sub-cell position.
        if piece.state == PieceState.MOVING and active_motions:
            motion = self._find_motion(piece, active_motions)
            if motion is not None:
                x, y = self._interpolator.get_pixel_position(motion)
            else:
                x, y = self._layout.cell_to_pixel(piece.position)
        else:
            x, y = self._layout.cell_to_pixel(piece.position)

        if piece.state == PieceState.AIRBORNE:
            y -= self._get_jump_height(
                elapsed_seconds=self._anim_controller.get_elapsed_seconds(
                    piece
                ),
                square_size=self._layout.square_size,
            )

        frame.draw_on(self._canvas.canvas, x, y)

    @staticmethod
    def _get_jump_height(
        elapsed_seconds: float,
        square_size: int,
    ) -> int:
        """Returns a smooth up-and-down height for one jump."""
        duration_seconds = JUMP_DURATION_MILLISECONDS / 1000
        progress = min(elapsed_seconds / duration_seconds, 1.0)
        peak_height = square_size * 0.35
        return round(sin(pi * progress) * peak_height)

    @staticmethod
    def _find_motion(
        piece: Piece,
        motions: tuple[Motion, ...],
    ) -> Motion | None:
        """Returns the active Motion for this piece, or None."""
        for motion in motions:
            if motion.piece is piece:
                return motion
        return None
