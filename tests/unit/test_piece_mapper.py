import unittest

from model.piece import PieceColor, PieceType
from model.piece_mapper import PieceMapper


class TestPieceMapperFromCode(unittest.TestCase):

    def test_white_pawn(self):
        result = PieceMapper.from_code("wP")
        self.assertEqual(result, (PieceType.PAWN, PieceColor.WHITE))

    def test_black_rook(self):
        result = PieceMapper.from_code("bR")
        self.assertEqual(result, (PieceType.ROOK, PieceColor.BLACK))

    def test_empty_square_returns_none(self):
        self.assertIsNone(PieceMapper.from_code("."))

    def test_all_piece_types(self):
        for code, expected_type in [
            ("wK", PieceType.KING),
            ("wQ", PieceType.QUEEN),
            ("wR", PieceType.ROOK),
            ("wB", PieceType.BISHOP),
            ("wN", PieceType.KNIGHT),
            ("wP", PieceType.PAWN),
        ]:
            with self.subTest(code=code):
                piece_type, _ = PieceMapper.from_code(code)
                self.assertEqual(piece_type, expected_type)


class TestPieceMapperToCode(unittest.TestCase):

    def test_none_returns_dot(self):
        self.assertEqual(PieceMapper.to_code(None), ".")

    def test_white_king(self):
        from board_io.text_board_parser import TextBoardParser
        from model.position import Position

        board = TextBoardParser.parse(["wK"])
        piece = board.get_piece(Position(0, 0))
        self.assertEqual(PieceMapper.to_code(piece), "wK")

    def test_black_bishop(self):
        from board_io.text_board_parser import TextBoardParser
        from model.position import Position

        board = TextBoardParser.parse(["bB"])
        piece = board.get_piece(Position(0, 0))
        self.assertEqual(PieceMapper.to_code(piece), "bB")

    def test_round_trip_all_pieces(self):
        from board_io.text_board_parser import TextBoardParser
        from model.position import Position

        codes = ["wK", "wQ", "wR", "wB", "wN", "wP",
                 "bK", "bQ", "bR", "bB", "bN", "bP"]
        row = " ".join(codes)
        board = TextBoardParser.parse([row])
        for col, expected_code in enumerate(codes):
            with self.subTest(code=expected_code):
                piece = board.get_piece(Position(0, col))
                self.assertEqual(PieceMapper.to_code(piece), expected_code)


if __name__ == "__main__":
    unittest.main()
