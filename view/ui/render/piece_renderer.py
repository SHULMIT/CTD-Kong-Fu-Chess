"""Draw piece frames produced by :class:`PieceAnimationService`."""

from model.piece import Piece
from realtime.motion import Motion
from view.ui.animation.animation_repository import AnimationRepository
from view.ui.animation.piece_animation_service import PieceAnimationService
from view.ui.layout.board_layout import BoardLayout
from view.ui.window.game_canvas import GameCanvas


class PieceRenderer:
    """Draws chess pieces on the game canvas one frame at a time."""

    def __init__(self, canvas: GameCanvas, layout: BoardLayout,
                 repository: AnimationRepository) -> None:
        self._canvas = canvas
        self._animation_service = PieceAnimationService(layout, repository)

    def draw(self, piece: Piece,
             active_motions: tuple[Motion, ...] | None = None) -> None:
        render_state = self._animation_service.get_render_state(piece, active_motions)
        if render_state is not None:
            render_state.frame.draw_on(self._canvas.canvas, render_state.x, render_state.y)
