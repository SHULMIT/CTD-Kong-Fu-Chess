import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.board import Board
from core.game import Game
from core.clock import Clock
from core.position import Position
from config.constants import EMPTY_SQUARE


def make_game(grid):
    """עוזר: יוצר אובייקט Game מרשת נתונה."""
    return Game(Board([row[:] for row in grid]))


# ---------------------------------------------------------------------------
# בדיקות Clock
# ---------------------------------------------------------------------------

class TestClock(unittest.TestCase):

    # בדיקה: שעון מתחיל מאפס.
    def test_initial_time_is_zero(self):
        clock = Clock()
        self.assertEqual(clock.current_time, 0)

    # בדיקה: tick מוסיף זמן נכון.
    def test_tick_accumulates_time(self):
        clock = Clock()
        clock.tick(100)
        clock.tick(250)
        self.assertEqual(clock.current_time, 350)

    # בדיקה: tick עם אפס מותר ולא משנה את הזמן.
    def test_tick_zero_is_allowed(self):
        clock = Clock()
        clock.tick(0)
        self.assertEqual(clock.current_time, 0)

    # בדיקה: tick עם ערך שלילי זורק ValueError.
    def test_tick_negative_raises(self):
        clock = Clock()
        with self.assertRaises(ValueError):
            clock.tick(-1)


# ---------------------------------------------------------------------------
# בדיקות Game — click ו-selection
# ---------------------------------------------------------------------------

class TestGameClick(unittest.TestCase):

    # בדיקה: לחיצה על משבצת ריקה לא בוחרת כלום.
    def test_click_empty_square_does_not_select(self):
        grid = [[EMPTY_SQUARE, "wP"]]
        game = make_game(grid)
        game.click(0, 0)   # עמודה 0, שורה 0 — ריק
        self.assertIsNone(game.selected_position)

    # בדיקה: לחיצה על כלי בוחרת אותו.
    def test_click_piece_selects_it(self):
        grid = [[EMPTY_SQUARE, "wP"]]
        game = make_game(grid)
        game.click(100, 0)  # עמודה 1, שורה 0 — "wP"
        self.assertEqual(game.selected_position, Position(0, 1))

    # בדיקה: לחיצה מחוץ לגבולות הלוח לא זורקת שגיאה ולא משנה מצב.
    def test_click_outside_board_is_ignored(self):
        grid = [["wP"]]
        game = make_game(grid)
        game.click(500, 500)  # הרבה מחוץ ללוח 1x1
        self.assertIsNone(game.selected_position)

    # בדיקה: לחיצה על כלי שני מאחר שנבחר כלי ראשון — מחליפה את הבחירה.
    def test_click_own_piece_switches_selection(self):
        grid = [["wP", "wR"]]
        game = make_game(grid)
        game.click(0, 0)    # בוחרת wP
        game.click(100, 0)  # מחליפה לwR
        self.assertEqual(game.selected_position, Position(0, 1))

    # בדיקה: לחיצה על משבצת ריקה אחרי בחירה — מזיזה את הכלי.
    # משתמשים ב-wR (צריח) כי הוא מממש can_move ויכול לזוז אופקית.
    def test_click_empty_after_selection_moves_piece(self):
        grid = [["wR", EMPTY_SQUARE]]
        game = make_game(grid)
        game.click(0, 0)    # בוחרת wR
        game.click(100, 0)  # זזה משבצת ימינה (תנועה אופקית — חוקית לצריח)
        self.assertEqual(game.board.get_piece(Position(0, 1)), "wR")
        self.assertEqual(game.board.get_piece(Position(0, 0)), EMPTY_SQUARE)

    # בדיקה: אחרי הזזה חוקית, selection מתאפס.
    def test_selection_cleared_after_move(self):
        grid = [["wR", EMPTY_SQUARE]]
        game = make_game(grid)
        game.click(0, 0)
        game.click(100, 0)
        self.assertIsNone(game.selected_position)

    # בדיקה: לחיצה על כלי יריב אחרי בחירה — אוכל אותו (מזיז לתוכו).
    # משתמשים ב-wR שיוכל לאכול את bR אופקית (תנועה חוקית לצריח).
    def test_click_enemy_piece_captures_it(self):
        grid = [["wR", "bR"]]
        game = make_game(grid)
        game.click(0, 0)    # בוחרת wR
        game.click(100, 0)  # אוכלת bR (תנועה אופקית — חוקית)
        self.assertEqual(game.board.get_piece(Position(0, 1)), "wR")
        self.assertEqual(game.board.get_piece(Position(0, 0)), EMPTY_SQUARE)


# ---------------------------------------------------------------------------
# בדיקות Game — wait
# ---------------------------------------------------------------------------

class TestGameWait(unittest.TestCase):

    # בדיקה: wait מקדם את שעון המשחק.
    def test_wait_advances_clock(self):
        grid = [["wP"]]
        game = make_game(grid)
        game.wait(300)
        self.assertEqual(game.clock.current_time, 300)

    # בדיקה: wait עם ערך שלילי זורק ValueError.
    def test_wait_negative_raises(self):
        grid = [["wP"]]
        game = make_game(grid)
        with self.assertRaises(ValueError):
            game.wait(-50)


if __name__ == "__main__":
    unittest.main()
