"""
Tests for game.game_query_service.
"""

from unittest.mock import MagicMock
import unittest

from game.game_query_service import GameQueryService


class TestGameQueryService(unittest.TestCase):
    def test_board_property_returns_injected_board(self):
        board = MagicMock()
        service = GameQueryService(board=board)

        self.assertIs(service.board, board)

    def test_is_inside_delegates_to_board(self):
        board = MagicMock()
        board.is_inside.return_value = True
        service = GameQueryService(board=board)
        position = MagicMock()

        self.assertTrue(service.is_inside(position))
        board.is_inside.assert_called_once_with(position)

    def test_get_piece_delegates_to_board(self):
        board = MagicMock()
        piece = MagicMock()
        board.get_piece.return_value = piece
        service = GameQueryService(board=board)
        position = MagicMock()

        self.assertIs(service.get_piece(position), piece)
        board.get_piece.assert_called_once_with(position)

    def test_has_piece_false_for_none(self):
        board = MagicMock()
        board.get_piece.return_value = None
        service = GameQueryService(board=board)

        self.assertFalse(service.has_piece(MagicMock()))

    def test_has_piece_false_for_empty_cell(self):
        board = MagicMock()
        board.EMPTY_CELL = "."
        board.get_piece.return_value = "."
        service = GameQueryService(board=board)

        self.assertFalse(service.has_piece(MagicMock()))

    def test_has_piece_true_for_actual_piece(self):
        board = MagicMock()
        board.EMPTY_CELL = "."
        board.get_piece.return_value = MagicMock()
        service = GameQueryService(board=board)

        self.assertTrue(service.has_piece(MagicMock()))