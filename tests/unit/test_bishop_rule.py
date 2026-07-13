import unittest

from board_io.text_board_parser import TextBoardParser
from model.position import Position
from rules.bishop_rule import BishopRule


def _board(text: str):
    return TextBoardParser.parse(text.strip().splitlines())


def _bishop(board, row, col):
    return board.get_piece(Position(row, col))


class TestBishopRuleOpenBoard(unittest.TestCase):

    def setUp(self):
        self.board = _board(
            ". . . . .\n"
            ". . . . .\n"
            ". . wB . .\n"
            ". . . . .\n"
            ". . . . ."
        )
        self.rule = BishopRule()
        self.bishop = _bishop(self.board, 2, 2)

    def test_moves_diagonally(self):
        moves = self.rule.get_legal_moves(self.bishop, self.board)
        self.assertIn(Position(0, 0), moves)
        self.assertIn(Position(0, 4), moves)
        self.assertIn(Position(4, 0), moves)
        self.assertIn(Position(4, 4), moves)

    def test_cannot_move_orthogonally(self):
        moves = self.rule.get_legal_moves(self.bishop, self.board)
        self.assertNotIn(Position(2, 0), moves)
        self.assertNotIn(Position(0, 2), moves)


class TestBishopRuleBlocked(unittest.TestCase):

    def setUp(self):
        self.rule = BishopRule()

    def test_blocked_by_friendly_piece(self):
        board = _board(
            ". . . . .\n"
            ". wP . . .\n"
            "wB . . . .\n"
            ". . . . .\n"
            ". . . . ."
        )
        bishop = _bishop(board, 2, 0)
        moves = self.rule.get_legal_moves(bishop, board)
        self.assertNotIn(Position(1, 1), moves)

    def test_can_capture_enemy_piece(self):
        board = _board(
            ". . . . .\n"
            ". bP . . .\n"
            "wB . . . .\n"
            ". . . . .\n"
            ". . . . ."
        )
        bishop = _bishop(board, 2, 0)
        moves = self.rule.get_legal_moves(bishop, board)
        self.assertIn(Position(1, 1), moves)
        self.assertNotIn(Position(0, 2), moves)


if __name__ == "__main__":
    unittest.main()
