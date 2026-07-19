"""Draws every piece currently present on the board."""

from model.board import Board
from model.piece import Piece
from model.position import Position
from realtime.motion import Motion
from view.ui.render.piece_renderer import PieceRenderer


class PieceLayerRenderer:
    """Coordinates rendering of all pieces in one scene frame."""

    def __init__(self, piece_renderer: PieceRenderer) -> None:
        self._piece_renderer = piece_renderer

    def draw(
        self,
        board: Board,
        active_motions: tuple[Motion, ...],
    ) -> None:
        """Draw every piece on the board using the active motion snapshot."""
        for row in range(board.height):
            for column in range(board.width):
                piece = board.get_piece(Position(row, column))
                if isinstance(piece, Piece):
                    self._piece_renderer.draw(piece, active_motions)
