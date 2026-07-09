import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.board import Board
from core.game import Game
from core.position import Position
from config.constants import EMPTY_SQUARE


def make_empty_board(size=8):
    return Board([[EMPTY_SQUARE for _ in range(size)] for _ in range(size)])


class TestPawnRules(unittest.TestCase):

    def test_white_pawn_can_double_move_from_start_row(self):
        board = make_empty_board()
        board.set_piece(Position(6, 3), "wP")
        game = Game(board)

        game.click(350, 650)
        game.click(350, 450)
        game.wait(2000)

        self.assertEqual(game.board.get_piece(Position(4, 3)), "wP")
        self.assertEqual(game.board.get_piece(Position(6, 3)), EMPTY_SQUARE)

    def test_pawn_double_move_is_blocked_by_piece_in_path(self):
        board = make_empty_board()
        board.set_piece(Position(6, 3), "wP")
        board.set_piece(Position(5, 3), "bR")
        game = Game(board)

        game.click(350, 650)
        game.click(350, 450)
        game.wait(2000)

        self.assertEqual(game.board.get_piece(Position(6, 3)), "wP")
        self.assertEqual(game.board.get_piece(Position(4, 3)), EMPTY_SQUARE)

    def test_pawn_promotes_to_queen_on_last_row(self):
        board = make_empty_board()
        board.set_piece(Position(1, 3), "bP")
        game = Game(board)

        game.click(350, 150)
        game.click(350, 50)
        game.wait(2000)

        self.assertEqual(game.board.get_piece(Position(0, 3)), "bQ")
        self.assertEqual(game.board.get_piece(Position(1, 3)), EMPTY_SQUARE)


if __name__ == "__main__":
    unittest.main()
