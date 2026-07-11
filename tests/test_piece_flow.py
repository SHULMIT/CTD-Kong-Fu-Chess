import unittest

from board_io.text_board_formatter import TextBoardFormatter
from board_io.text_board_parser import TextBoardParser
from model.piece import PieceColor, PieceType
from model.position import Position


class TestPieceFlow(unittest.TestCase):
    def test_parse_and_create_piece_flow(self):
        board_lines = [". wP", "bR ."]
        board = TextBoardParser.parse(board_lines)

        white_pawn = board.get_piece(Position(0, 1))
        black_rook = board.get_piece(Position(1, 0))
        empty_cell = board.get_piece(Position(1, 1))

        self.assertIsNotNone(white_pawn)
        self.assertEqual(white_pawn.type, PieceType.PAWN)
        self.assertEqual(white_pawn.color, PieceColor.WHITE)

        self.assertIsNotNone(black_rook)
        self.assertEqual(black_rook.type, PieceType.ROOK)
        self.assertEqual(black_rook.color, PieceColor.BLACK)

        self.assertIsNone(empty_cell)

    def test_formatter_round_trip_with_empty_cells(self):
        board_lines = [". wP", "bR ."]
        board = TextBoardParser.parse(board_lines)

        formatted = TextBoardFormatter.format(board)

        self.assertEqual(formatted, ". wP\nbR .")


if __name__ == "__main__":
    unittest.main()
