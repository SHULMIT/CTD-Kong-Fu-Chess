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


def make_game(grid):
    return Game(Board([row[:] for row in grid]))


class TestGameOver(unittest.TestCase):

    def test_capturing_enemy_king_ends_game(self):
        grid = [["wR", "bK"]]
        game = make_game(grid)

        game.click(0, 0)
        game.click(100, 0)
        game.wait(2000)

        self.assertTrue(game.game_over)
        self.assertEqual(game.board.get_piece(Position(0, 1)), "wR")

    def test_later_move_commands_are_ignored_after_game_over(self):
        grid = [["wR", "bK"]]
        game = make_game(grid)

        game.click(0, 0)
        game.click(100, 0)
        game.wait(2000)
        game.click(0, 0)
        game.click(100, 0)
        game.wait(1000)

        self.assertTrue(game.game_over)
        self.assertEqual(game.board.get_piece(Position(0, 1)), "wR")
        self.assertEqual(game.board.get_piece(Position(0, 0)), EMPTY_SQUARE)


if __name__ == "__main__":
    unittest.main()
