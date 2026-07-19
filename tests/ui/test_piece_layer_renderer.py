"""Tests for rendering the complete board piece layer."""

from unittest.mock import Mock

from model.board import Board
from model.piece import Piece, PieceColor, PieceType
from model.position import Position
from view.ui.render.piece_layer_renderer import PieceLayerRenderer


def test_piece_layer_draws_only_piece_instances_with_active_motions() -> None:
    piece = Piece(1, PieceType.ROOK, PieceColor.WHITE, Position(0, 1))
    board = Board([[Board.EMPTY_CELL, piece], [None, Board.EMPTY_CELL]])
    active_motions = ()
    piece_renderer = Mock()

    PieceLayerRenderer(piece_renderer).draw(board, active_motions)

    piece_renderer.draw.assert_called_once_with(piece, active_motions)
