"""Resolve the visual render state for a single piece."""

from dataclasses import dataclass
from math import pi, sin

from config.constants import (
    JUMP_DURATION_MILLISECONDS,
    JUMP_HEIGHT_RATIO,
    MILLISECONDS_PER_SECOND,
)
from model.piece import Piece, PieceState
from realtime.motion import Motion
from view.ui.animation.animation_repository import AnimationRepository
from view.ui.animation.animation_state import AnimationState
from view.ui.animation.animation_state_resolver import AnimationStateResolver
from view.ui.animation.piece_animation_controller import PieceAnimationController
from view.ui.animation.piece_code_resolver import PieceCodeResolver
from view.ui.graphics.img import Img as AnimationFrame
from view.ui.layout.board_layout import BoardLayout
from view.ui.layout.motion_interpolator import MotionInterpolator


@dataclass(frozen=True)
class PieceRenderState:
    frame: AnimationFrame
    x: float
    y: float


class PieceAnimationService:
    """Calculates the complete visual state of a piece."""

    def __init__(self, layout: BoardLayout, repository: AnimationRepository,
                 animation_controller: PieceAnimationController | None = None) -> None:
        self._layout = layout
        self._repository = repository
        self._interpolator = MotionInterpolator(layout)
        self._anim_controller = animation_controller or PieceAnimationController()

    def get_render_state(self, piece: Piece,
                         active_motions: tuple[Motion, ...] | None = None
                         ) -> PieceRenderState | None:
        if piece.state == PieceState.CAPTURED:
            self._anim_controller.reset(piece)
            return None

        piece_code = PieceCodeResolver.resolve(piece)
        anim_state = AnimationStateResolver.resolve(piece.state)
        try:
            animation = self._repository.get(
                piece_code=piece_code, state=anim_state,
                size=(self._layout.square_size, self._layout.square_size))
        except (FileNotFoundError, OSError):
            animation = self._repository.get(
                piece_code=piece_code, state=AnimationState.IDLE,
                size=(self._layout.square_size, self._layout.square_size))

        frame = animation.frames[self._anim_controller.get_frame_index(piece, animation)]
        x, y = self._layout.cell_to_pixel(piece.position)
        if piece.state == PieceState.MOVING and active_motions:
            motion = self._find_motion(piece, active_motions)
            if motion is not None:
                x, y = self._interpolator.get_pixel_position(motion)
        if piece.state == PieceState.AIRBORNE:
            y -= self._get_jump_height(
                self._anim_controller.get_elapsed_seconds(piece), self._layout.square_size)
        return PieceRenderState(frame=frame, x=x, y=y)

    @staticmethod
    def _get_jump_height(elapsed_seconds: float, square_size: int) -> int:
        """Return the height for the same duration used by AirborneManager."""
        duration_seconds = JUMP_DURATION_MILLISECONDS / MILLISECONDS_PER_SECOND
        progress = min(elapsed_seconds / duration_seconds, 1.0)
        return round(sin(pi * progress) * square_size * JUMP_HEIGHT_RATIO)

    @staticmethod
    def _find_motion(piece: Piece, motions: tuple[Motion, ...]) -> Motion | None:
        return next((motion for motion in motions if motion.piece is piece), None)
