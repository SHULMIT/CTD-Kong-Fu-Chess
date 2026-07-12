import unittest

from board_io.text_board_parser import TextBoardParser
from model.position import Position
from rules.king_rule import KingRule


def _board(text: str):
    return TextBoardParser.parse(text.strip().splitlines())


def _king(board, row, col):
    return board.get_piece(Position(row, col))


class TestKingRuleOpenBoard(unittest.TestCase):

    def setUp(self):
        self.board = _board(
            ". . . . .\n"
            ". . . . .\n"
            ". . wK . .\n"
            ". . . . .\n"
            ". . . . ."
        )
        self.rule = KingRule()
        self.king = _king(self.board, 2, 2)

    def test_moves_exactly_one_step_in_all_directions(self):
        moves = self.rule.get_legal_moves(self.king, self.board)
        expected = {
            Position(1, 1), Position(1, 2), Position(1, 3),
            Position(2, 1),                 Position(2, 3),
            Position(3, 1), Position(3, 2), Position(3, 3),
        }
        self.assertEqual(moves, expected)

    def test_cannot_stay_in_place(self):
        moves = self.rule.get_legal_moves(self.king, self.board)
        self.assertNotIn(Position(2, 2), moves)


class TestKingRuleEdgeAndCorner(unittest.TestCase):

    def setUp(self):
        self.rule = KingRule()

    def test_king_in_corner_has_three_moves(self):
        board = _board(
            "wK . .\n"
            ". . .\n"
            ". . ."
        )
        king = _king(board, 0, 0)
        moves = self.rule.get_legal_moves(king, board)
        self.assertEqual(len(moves), 3)

    def test_blocked_by_friendly_pieces(self):
        board = _board(
            "wK wP .\n"
            "wP wP .\n"
            ". . ."
        )
        king = _king(board, 0, 0)
        moves = self.rule.get_legal_moves(king, board)
        self.assertEqual(moves, set())

    def test_can_capture_enemy(self):
        board = _board(
            "wK bP .\n"
            ". . .\n"
            ". . ."
        )
        king = _king(board, 0, 0)
        moves = self.rule.get_legal_moves(king, board)
        self.assertIn(Position(0, 1), moves)


if __name__ == "__main__":
    unittest.main()
