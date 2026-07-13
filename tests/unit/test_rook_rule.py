import unittest

from board_io.text_board_parser import TextBoardParser
from model.position import Position
from rules.rook_rule import RookRule


def _board(text: str):
    return TextBoardParser.parse(text.strip().splitlines())


def _rook(board, row, col):
    return board.get_piece(Position(row, col))


class TestRookRuleOpenBoard(unittest.TestCase):

    def setUp(self):
        self.board = _board(
            ". . . . .\n"
            ". . . . .\n"
            ". . wR . .\n"
            ". . . . .\n"
            ". . . . ."
        )
        self.rule = RookRule()
        self.rook = _rook(self.board, 2, 2)

    def test_moves_along_entire_row(self):
        moves = self.rule.get_legal_moves(self.rook, self.board)
        for col in [0, 1, 3, 4]:
            self.assertIn(Position(2, col), moves)

    def test_moves_along_entire_column(self):
        moves = self.rule.get_legal_moves(self.rook, self.board)
        for row in [0, 1, 3, 4]:
            self.assertIn(Position(row, 2), moves)

    def test_cannot_stay_in_place(self):
        moves = self.rule.get_legal_moves(self.rook, self.board)
        self.assertNotIn(Position(2, 2), moves)


class TestRookRuleBlocked(unittest.TestCase):

    def setUp(self):
        self.rule = RookRule()

    def test_blocked_by_friendly_piece(self):
        board = _board(
            "wR wP . . ."
        )
        rook = _rook(board, 0, 0)
        moves = self.rule.get_legal_moves(rook, board)
        # friendly piece at (0,1) — rook cannot go past it
        self.assertNotIn(Position(0, 1), moves)
        self.assertNotIn(Position(0, 2), moves)

    def test_can_capture_enemy_piece(self):
        board = _board(
            "wR . bP . ."
        )
        rook = _rook(board, 0, 0)
        moves = self.rule.get_legal_moves(rook, board)
        self.assertIn(Position(0, 2), moves)
        # cannot go past the captured piece
        self.assertNotIn(Position(0, 3), moves)


if __name__ == "__main__":
    unittest.main()
