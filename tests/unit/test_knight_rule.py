import unittest

from board_io.text_board_parser import TextBoardParser
from model.position import Position
from rules.knight_rule import KnightRule


def _board(text: str):
    return TextBoardParser.parse(text.strip().splitlines())


def _knight(board, row, col):
    return board.get_piece(Position(row, col))


class TestKnightRuleOpenBoard(unittest.TestCase):

    def setUp(self):
        self.board = _board(
            ". . . . . .\n"
            ". . . . . .\n"
            ". . wN . . .\n"
            ". . . . . .\n"
            ". . . . . .\n"
            ". . . . . ."
        )
        self.rule = KnightRule()
        self.knight = _knight(self.board, 2, 2)

    def test_all_eight_l_shapes(self):
        moves = self.rule.get_legal_moves(self.knight, self.board)
        expected = {
            Position(0, 1), Position(0, 3),
            Position(1, 0), Position(1, 4),
            Position(3, 0), Position(3, 4),
            Position(4, 1), Position(4, 3),
        }
        self.assertEqual(moves, expected)

    def test_jumps_over_pieces(self):
        board = _board(
            ". . . . . .\n"
            ". wP wP . . .\n"
            ". wP wN wP . .\n"
            ". wP wP . . .\n"
            ". . . . . .\n"
            ". . . . . ."
        )
        knight = _knight(board, 2, 2)
        moves = self.rule.get_legal_moves(knight, board)
        # knight jumps over the surrounding pawns
        self.assertIn(Position(0, 1), moves)
        self.assertIn(Position(4, 3), moves)


class TestKnightRuleEdge(unittest.TestCase):

    def setUp(self):
        self.rule = KnightRule()

    def test_corner_knight_has_two_moves(self):
        board = _board(
            "wN . . . .\n"
            ". . . . .\n"
            ". . . . .\n"
            ". . . . .\n"
            ". . . . ."
        )
        knight = _knight(board, 0, 0)
        moves = self.rule.get_legal_moves(knight, board)
        self.assertEqual(moves, {Position(1, 2), Position(2, 1)})

    def test_blocked_by_friendly_piece(self):
        board = _board(
            "wN . . . .\n"
            ". . wP . .\n"
            ". wP . . .\n"
            ". . . . .\n"
            ". . . . ."
        )
        knight = _knight(board, 0, 0)
        moves = self.rule.get_legal_moves(knight, board)
        self.assertEqual(moves, set())


if __name__ == "__main__":
    unittest.main()
