import unittest

from board_io.text_board_parser import TextBoardParser
from model.position import Position
from rules.queen_rule import QueenRule


def _board(text: str):
    return TextBoardParser.parse(text.strip().splitlines())


def _queen(board, row, col):
    return board.get_piece(Position(row, col))


class TestQueenRuleOpenBoard(unittest.TestCase):

    def setUp(self):
        self.board = _board(
            ". . . . .\n"
            ". . . . .\n"
            ". . wQ . .\n"
            ". . . . .\n"
            ". . . . ."
        )
        self.rule = QueenRule()
        self.queen = _queen(self.board, 2, 2)

    def test_moves_orthogonally(self):
        moves = self.rule.get_legal_moves(self.queen, self.board)
        for col in [0, 1, 3, 4]:
            self.assertIn(Position(2, col), moves)
        for row in [0, 1, 3, 4]:
            self.assertIn(Position(row, 2), moves)

    def test_moves_diagonally(self):
        moves = self.rule.get_legal_moves(self.queen, self.board)
        self.assertIn(Position(0, 0), moves)
        self.assertIn(Position(0, 4), moves)
        self.assertIn(Position(4, 0), moves)
        self.assertIn(Position(4, 4), moves)

    def test_cannot_stay_in_place(self):
        moves = self.rule.get_legal_moves(self.queen, self.board)
        self.assertNotIn(Position(2, 2), moves)


class TestQueenRuleBlocked(unittest.TestCase):

    def setUp(self):
        self.rule = QueenRule()

    def test_blocked_by_friendly_piece(self):
        board = _board(
            "wQ wP . . ."
        )
        queen = _queen(board, 0, 0)
        moves = self.rule.get_legal_moves(queen, board)
        self.assertNotIn(Position(0, 1), moves)
        self.assertNotIn(Position(0, 4), moves)

    def test_can_capture_enemy_piece(self):
        board = _board(
            "wQ . bP . ."
        )
        queen = _queen(board, 0, 0)
        moves = self.rule.get_legal_moves(queen, board)
        self.assertIn(Position(0, 2), moves)
        self.assertNotIn(Position(0, 3), moves)


if __name__ == "__main__":
    unittest.main()
