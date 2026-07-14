from model.piece import Piece

from view.ui.animation.animation_repository import AnimationRepository
from view.ui.animation.animation_state import AnimationState
from view.ui.animation.piece_code_resolver import PieceCodeResolver
from view.ui.layout.board_layout import BoardLayout
from view.ui.window.game_canvas import GameCanvas


class PieceRenderer:
    """
    Responsible for drawing a single chess piece.
    """

    def __init__(
            self,
            canvas: GameCanvas,
            layout: BoardLayout,
            repository: AnimationRepository
    ):

        self._canvas = canvas
        self._layout = layout
        self._repository = repository

    def draw(self, piece: Piece) -> None:
        """
        Draws a single chess piece.
        """

        piece_code = PieceCodeResolver.resolve(piece)

        animation = self._repository.get(
            piece_code=piece_code,
            state=AnimationState.IDLE,
            size=(
                self._layout.square_size,
                self._layout.square_size
            )
        )

        frame = animation.frames[0]

        x, y = self._layout.cell_to_pixel(
            piece.position
        )

        frame.draw_on(
            self._canvas.canvas,
            x,
            y
        )