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
from view.ui.animation.piece_animation_controller import (
    PieceAnimationController,
)
from view.ui.animation.piece_code_resolver import PieceCodeResolver
from view.ui.graphics.img import Img as AnimationFrame
from view.ui.layout.board_layout import BoardLayout
from view.ui.layout.motion_interpolator import MotionInterpolator


@dataclass(frozen=True)
class PieceRenderState:
    """Everything the renderer needs to draw one piece."""

    frame: AnimationFrame
    x: float
    y: float


class PieceAnimationService:
    """Builds the visual state of a piece for the current frame."""

    def __init__(
        self,
        layout: BoardLayout,
        repository: AnimationRepository,
        animation_controller: PieceAnimationController | None = None,
    ) -> None:
        self._layout = layout
        self._repository = repository
        self._interpolator = MotionInterpolator(layout)
        self._animation_controller = (
            animation_controller
            or PieceAnimationController()
        )

    def get_render_state(
        self,
        piece: Piece,
        active_motions: tuple[Motion, ...] | None = None,
    ) -> PieceRenderState | None:
        """
        Return everything needed to draw the piece.

        Captured pieces return None because they should not be drawn.
        """

        if self._is_hidden(piece):
            self._reset_animation(piece)
            return None

        frame = self._resolve_frame(piece)

        x, y = self._resolve_position(
            piece=piece,
            active_motions=active_motions,
        )

        return PieceRenderState(
            frame=frame,
            x=x,
            y=y,
        )

    def _is_hidden(self, piece: Piece) -> bool:
        """Return whether the piece should not be drawn."""

        return piece.state == PieceState.CAPTURED

    def _reset_animation(self, piece: Piece) -> None:
        """Forget the animation progress of a hidden piece."""

        self._animation_controller.reset(piece)

    def _resolve_frame(
        self,
        piece: Piece,
    ) -> AnimationFrame:
        """Return the animation frame that should currently be drawn."""

        animation = self._load_animation(piece)

        frame_index = self._animation_controller.get_frame_index(
            piece,
            animation,
        )

        return animation.frames[frame_index]

    def _load_animation(self, piece: Piece):
        """
        Load the animation matching the piece's current state.

        Fall back to the idle animation when the requested animation
        is unavailable.
        """

        piece_code = PieceCodeResolver.resolve(piece)
        animation_state = AnimationStateResolver.resolve(piece.state)

        try:
            return self._repository.get(
                piece_code=piece_code,
                state=animation_state,
                size=self._animation_size,
            )

        except (FileNotFoundError, OSError):
            return self._repository.get(
                piece_code=piece_code,
                state=AnimationState.IDLE,
                size=self._animation_size,
            )

    @property
    def _animation_size(self) -> tuple[int, int]:
        """Return the requested image size for piece animations."""

        square_size = self._layout.square_size
        return square_size, square_size

    def _resolve_position(
        self,
        piece: Piece,
        active_motions: tuple[Motion, ...] | None,
    ) -> tuple[float, float]:
        """Return the pixel position where the piece should be drawn."""

        x, y = self._get_board_position(piece)

        if piece.state == PieceState.MOVING:
            x, y = self._get_moving_position(
                piece=piece,
                active_motions=active_motions,
                fallback=(x, y),
            )

        if piece.state == PieceState.AIRBORNE:
            y = self._apply_jump_height(
                piece=piece,
                y=y,
            )

        return x, y

    def _get_board_position(
        self,
        piece: Piece,
    ) -> tuple[float, float]:
        """Convert the piece's board cell into pixel coordinates."""

        return self._layout.cell_to_pixel(piece.position)

    def _get_moving_position(
        self,
        piece: Piece,
        active_motions: tuple[Motion, ...] | None,
        fallback: tuple[float, float],
    ) -> tuple[float, float]:
        """
        Return the piece's interpolated movement position.

        If no matching motion exists, return its normal board position.
        """

        if not active_motions:
            return fallback

        motion = self._find_motion(
            piece=piece,
            motions=active_motions,
        )

        if motion is None:
            return fallback

        return self._interpolator.get_pixel_position(motion)

    def _apply_jump_height(
        self,
        piece: Piece,
        y: float,
    ) -> float:
        """Move an airborne piece upward according to jump progress."""

        elapsed_seconds = (
            self._animation_controller.get_elapsed_seconds(piece)
        )

        jump_height = self._calculate_jump_height(
            elapsed_seconds=elapsed_seconds,
            square_size=self._layout.square_size,
        )

        return y - jump_height

    @staticmethod
    def _calculate_jump_height(
        elapsed_seconds: float,
        square_size: int,
    ) -> int:
        """Calculate the current height of the jump arc."""

        duration_seconds = (
            JUMP_DURATION_MILLISECONDS
            / MILLISECONDS_PER_SECOND
        )

        progress = min(
            elapsed_seconds / duration_seconds,
            1.0,
        )

        height_ratio = sin(pi * progress)

        return round(
            height_ratio
            * square_size
            * JUMP_HEIGHT_RATIO
        )

    @staticmethod
    def _find_motion(
        piece: Piece,
        motions: tuple[Motion, ...],
    ) -> Motion | None:
        """Find the active motion belonging to the given piece."""

        return next(
            (
                motion
                for motion in motions
                if motion.piece is piece
            ),
            None,
        )