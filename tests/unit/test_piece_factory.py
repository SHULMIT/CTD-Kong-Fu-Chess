import unittest

from board_io.text_board_parser import TextBoardParser
from model.piece import PieceColor, PieceState, PieceType
from model.piece_factory import PieceFactory
from model.piece_mapper import PieceMapper
from model.position import Position


class TestPieceFactoryCreation(unittest.TestCase):

    def _make_piece(self, code: str):
        piece_data = PieceMapper.from_code(code)
        return PieceFactory.create_piece(
            piece_data=piece_data,
            position=Position(0, 0),
        )

    def test_returns_none_for_empty_square(self):
        result = PieceFactory.create_piece(
            piece_data=None,
            position=Position(0, 0),
        )
        self.assertIsNone(result)

    def test_piece_has_correct_type_and_color(self):
        piece = self._make_piece("wR")
        self.assertEqual(piece.type, PieceType.ROOK)
        self.assertEqual(piece.color, PieceColor.WHITE)

    def test_piece_has_correct_position(self):
        piece_data = PieceMapper.from_code("bQ")
        piece = PieceFactory.create_piece(
            piece_data=piece_data,
            position=Position(3, 5),
        )
        self.assertEqual(piece.position, Position(3, 5))

    def test_piece_initial_state_is_idle(self):
        piece = self._make_piece("wP")
        self.assertEqual(piece.state, PieceState.IDLE)

    def test_each_piece_gets_unique_id(self):
        p1 = self._make_piece("wR")
        p2 = self._make_piece("bR")
        self.assertNotEqual(p1.id, p2.id)


if __name__ == "__main__":
    unittest.main()
