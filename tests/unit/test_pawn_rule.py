import unittest

from board_io.text_board_parser import TextBoardParser
from model.position import Position
from rules.pawn_rule import PawnRule


def _board(text: str):
    return TextBoardParser.parse(text.strip().splitlines())


def _pawn(board, row, col):
    return board.get_piece(Position(row, col))


class TestWhitePawnForwardMove(unittest.TestCase):

    def setUp(self):
        self.rule = PawnRule()

    def test_single_step_forward(self):
        # white moves UP (row decreases)
        board = _board(
            ". . .\n"
            ". wP .\n"
            ". . ."
        )
        pawn = _pawn(board, 1, 1)
        moves = self.rule.get_legal_moves(pawn, board)
        self.assertIn(Position(0, 1), moves)

    def test_double_step_from_start_row(self):
        # White starts at row height - 2 (row 6 on a standard board).
        board = _board(
            ". . .\n"  # row 0
            ". . .\n"  # row 1
            ". . .\n"  # row 2
            ". . .\n"  # row 3
            ". . .\n"  # row 4
            ". . .\n"  # row 5
            ". wP .\n"  # row 6  ← white start row (height-2)
            ". . ."   # row 7
        )
        pawn = _pawn(board, 6, 1)
        moves = self.rule.get_legal_moves(pawn, board)
        self.assertIn(Position(4, 1), moves)

    def test_cannot_double_step_when_not_on_start_row(self):
        board = _board(
            ". . .\n"
            ". . .\n"
            ". wP .\n"
            ". . .\n"
            ". . ."
        )
        pawn = _pawn(board, 2, 1)
        moves = self.rule.get_legal_moves(pawn, board)
        self.assertNotIn(Position(0, 1), moves)

    def test_blocked_by_piece_directly_ahead(self):
        board = _board(
            ". . .\n"
            ". bR .\n"
            ". wP .\n"
            ". . ."
        )
        pawn = _pawn(board, 2, 1)
        moves = self.rule.get_legal_moves(pawn, board)
        self.assertNotIn(Position(1, 1), moves)

    def test_double_step_blocked_by_piece_in_middle(self):
        board = _board(
            ". . .\n"
            ". . .\n"
            ". . .\n"
            ". . .\n"
            ". . .\n"
            ". bR .\n"
            ". wP .\n"
            ". . ."
        )
        pawn = _pawn(board, 6, 1)
        moves = self.rule.get_legal_moves(pawn, board)
        self.assertNotIn(Position(4, 1), moves)


class TestWhitePawnDiagonalCapture(unittest.TestCase):

    def setUp(self):
        self.rule = PawnRule()

    def test_captures_diagonally(self):
        board = _board(
            "bR . bR\n"
            ". wP .\n"
            ". . ."
        )
        pawn = _pawn(board, 1, 1)
        moves = self.rule.get_legal_moves(pawn, board)
        self.assertIn(Position(0, 0), moves)
        self.assertIn(Position(0, 2), moves)

    def test_cannot_capture_empty_diagonal(self):
        board = _board(
            ". . .\n"
            ". wP .\n"
            ". . ."
        )
        pawn = _pawn(board, 1, 1)
        moves = self.rule.get_legal_moves(pawn, board)
        self.assertNotIn(Position(0, 0), moves)
        self.assertNotIn(Position(0, 2), moves)

    def test_cannot_capture_friendly_diagonal(self):
        board = _board(
            "wR . wR\n"
            ". wP .\n"
            ". . ."
        )
        pawn = _pawn(board, 1, 1)
        moves = self.rule.get_legal_moves(pawn, board)
        self.assertNotIn(Position(0, 0), moves)
        self.assertNotIn(Position(0, 2), moves)


class TestBlackPawnMovesDown(unittest.TestCase):

    def setUp(self):
        self.rule = PawnRule()

    def test_black_single_step_downward(self):
        board = _board(
            ". bP .\n"
            ". . .\n"
            ". . ."
        )
        pawn = _pawn(board, 0, 1)
        moves = self.rule.get_legal_moves(pawn, board)
        self.assertIn(Position(1, 1), moves)

    def test_black_double_step_from_start_row(self):
        board = _board(
            ". . .\n"  # row 0
            ". bP .\n"  # row 1  ← black start row
            ". . .\n"
            ". . ."
        )
        pawn = _pawn(board, 1, 1)
        moves = self.rule.get_legal_moves(pawn, board)
        self.assertIn(Position(3, 1), moves)

    def test_black_captures_diagonally_downward(self):
        board = _board(
            ". bP .\n"
            "wR . wR\n"
            ". . ."
        )
        pawn = _pawn(board, 0, 1)
        moves = self.rule.get_legal_moves(pawn, board)
        self.assertIn(Position(1, 0), moves)
        self.assertIn(Position(1, 2), moves)


if __name__ == "__main__":
    unittest.main()
