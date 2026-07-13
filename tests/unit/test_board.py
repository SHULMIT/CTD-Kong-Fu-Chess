import unittest

from board_io.text_board_parser import TextBoardParser
from model.board import Board
from model.position import Position


def _make_board(text: str) -> Board:
    return TextBoardParser.parse(text.strip().splitlines())


class TestBoardDimensions(unittest.TestCase):

    def test_width_and_height(self):
        board = _make_board(". . .\n. . .")
        self.assertEqual(board.width, 3)
        self.assertEqual(board.height, 2)

    def test_empty_board(self):
        board = Board([])
        self.assertEqual(board.width, 0)
        self.assertEqual(board.height, 0)


class TestBoardIsInside(unittest.TestCase):

    def setUp(self):
        self.board = _make_board(". .\n. .")

    def test_corner_is_inside(self):
        self.assertTrue(self.board.is_inside(Position(0, 0)))
        self.assertTrue(self.board.is_inside(Position(1, 1)))

    def test_negative_row_is_outside(self):
        self.assertFalse(self.board.is_inside(Position(-1, 0)))

    def test_negative_column_is_outside(self):
        self.assertFalse(self.board.is_inside(Position(0, -1)))

    def test_row_out_of_bounds(self):
        self.assertFalse(self.board.is_inside(Position(2, 0)))

    def test_column_out_of_bounds(self):
        self.assertFalse(self.board.is_inside(Position(0, 2)))


class TestBoardGetPiece(unittest.TestCase):

    def test_empty_cell_returns_none(self):
        board = _make_board(". wR\n. .")
        self.assertIsNone(board.get_piece(Position(0, 0)))

    def test_piece_cell_returns_piece(self):
        board = _make_board(". wR\n. .")
        piece = board.get_piece(Position(0, 1))
        self.assertIsNotNone(piece)

    def test_out_of_bounds_raises(self):
        board = _make_board(". .")
        with self.assertRaises(IndexError):
            board.get_piece(Position(5, 5))


class TestBoardSetPiece(unittest.TestCase):

    def test_set_piece_replaces_content(self):
        board = _make_board(". .\n. .")
        original_piece = TextBoardParser.parse(["wR ."]).get_piece(Position(0, 0))
        board.set_piece(Position(0, 0), original_piece)
        self.assertIsNotNone(board.get_piece(Position(0, 0)))

    def test_set_none_clears_cell(self):
        board = _make_board("wR .")
        board.set_piece(Position(0, 0), None)
        self.assertIsNone(board.get_piece(Position(0, 0)))

    def test_set_out_of_bounds_raises(self):
        board = _make_board(". .")
        with self.assertRaises(IndexError):
            board.set_piece(Position(9, 9), None)


if __name__ == "__main__":
    unittest.main()
