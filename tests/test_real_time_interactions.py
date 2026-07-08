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


class TestRealTimeInteractions(unittest.TestCase):

    def test_enemy_collision_white_started_first(self):
        grid = [["wR", EMPTY_SQUARE, EMPTY_SQUARE, "bR"]]
        game = make_game(grid)

        game.click(50, 50)
        game.click(350, 50)
        game.click(350, 50)
        game.click(50, 50)
        game.wait(3000)

        self.assertEqual(game.board.get_piece(Position(0, 0)), EMPTY_SQUARE)
        self.assertEqual(game.board.get_piece(Position(0, 3)), "wR")

    def test_enemy_collision_black_started_first(self):
        grid = [["wR", EMPTY_SQUARE, EMPTY_SQUARE, "bR"]]
        game = make_game(grid)

        game.click(350, 50)
        game.click(50, 50)
        game.click(50, 50)
        game.click(350, 50)
        game.wait(3000)

        self.assertEqual(game.board.get_piece(Position(0, 3)), EMPTY_SQUARE)
        self.assertEqual(game.board.get_piece(Position(0, 0)), "bR")

    def test_cannot_start_move_through_friendly_piece(self):
        grid = [
            [EMPTY_SQUARE, EMPTY_SQUARE, EMPTY_SQUARE],
            ["wR", "wP", EMPTY_SQUARE],
            [EMPTY_SQUARE, EMPTY_SQUARE, EMPTY_SQUARE],
        ]
        game = make_game(grid)

        game.click(50, 150)
        game.click(250, 150)
        game.wait(2000)

        self.assertEqual(game.board.get_piece(Position(1, 0)), "wR")
        self.assertEqual(game.board.get_piece(Position(1, 1)), "wP")

    def test_dynamic_block_tactic_not_in_common_route(self):
        grid = [
            [EMPTY_SQUARE, EMPTY_SQUARE, EMPTY_SQUARE, EMPTY_SQUARE],
            ["wQ", EMPTY_SQUARE, EMPTY_SQUARE, "bK"],
            [EMPTY_SQUARE, EMPTY_SQUARE, "bP", EMPTY_SQUARE],
            [EMPTY_SQUARE, EMPTY_SQUARE, EMPTY_SQUARE, EMPTY_SQUARE],
        ]
        game = make_game(grid)

        game.click(50, 150)
        game.click(350, 150)
        game.wait(200)
        game.click(250, 250)
        game.click(250, 150)
        game.wait(3000)

        self.assertEqual(game.board.get_piece(Position(1, 3)), "wQ")
        self.assertEqual(game.board.get_piece(Position(2, 2)), "bP")

    def test_knight_cannot_land_on_friendly_piece(self):
        grid = [
            [EMPTY_SQUARE, "wP", EMPTY_SQUARE],
            [EMPTY_SQUARE, EMPTY_SQUARE, EMPTY_SQUARE],
            ["wN", EMPTY_SQUARE, EMPTY_SQUARE],
        ]
        game = make_game(grid)

        game.click(50, 250)
        game.click(150, 50)
        game.wait(1000)

        self.assertEqual(game.board.get_piece(Position(2, 0)), "wN")
        self.assertEqual(game.board.get_piece(Position(0, 1)), "wP")

    def test_premove_does_not_execute_in_common_route(self):
        grid = [["wR", EMPTY_SQUARE, EMPTY_SQUARE]]
        game = make_game(grid)

        game.click(50, 50)
        game.click(150, 50)
        game.click(50, 50)
        game.click(250, 50)
        game.wait(2000)

        self.assertEqual(game.board.get_piece(Position(0, 0)), EMPTY_SQUARE)
        self.assertEqual(game.board.get_piece(Position(0, 1)), "wR")


if __name__ == "__main__":
    unittest.main()
