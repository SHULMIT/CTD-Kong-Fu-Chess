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
        grid = [[EMPTY_SQUARE, "wK"]]
        game = make_game(grid)
        game.click(0, 0)
        self.assertIsNone(game.selected_position)

    # בדיקה: לחיצה על כלי בוחרת אותו.
    def test_click_piece_selects_it(self):
        grid = [[EMPTY_SQUARE, "wK"]]
        game = make_game(grid)
        game.click(100, 0)
        self.assertEqual(game.selected_position, Position(0, 1))

    # בדיקה: לחיצה מחוץ לגבולות הלוח לא זורקת שגיאה ולא משנה מצב.
    def test_click_outside_board_is_ignored(self):
        grid = [["wK"]]
        game = make_game(grid)
        game.click(500, 500)
        self.assertIsNone(game.selected_position)

    # בדיקה: לחיצה על כלי שני מאחר שנבחר כלי ראשון — מחליפה את הבחירה.
    def test_click_own_piece_switches_selection(self):
        grid = [["wK", "wR"]]
        game = make_game(grid)
        game.click(0, 0)    # בוחרת wK
        game.click(100, 0)  # מחליפה ל-wR
        self.assertEqual(game.selected_position, Position(0, 1))

    # בדיקה: אחרי click תקין, הכלי עדיין לא זז — רק אחרי wait.
    def test_piece_does_not_move_before_wait(self):
        grid = [["wK", EMPTY_SQUARE]]
        game = make_game(grid)
        game.click(0, 0)
        game.click(100, 0)
        # לפני wait — הכלי עדיין במקורו
        self.assertEqual(game.board.get_piece(Position(0, 0)), "wK")

    # בדיקה: אחרי wait, הכלי עובר ליעד.
    def test_piece_moves_after_wait(self):
        grid = [["wK", EMPTY_SQUARE]]
        game = make_game(grid)
        game.click(0, 0)
        game.click(100, 0)
        game.wait(1000)
        self.assertEqual(game.board.get_piece(Position(0, 1)), "wK")
        self.assertEqual(game.board.get_piece(Position(0, 0)), EMPTY_SQUARE)

    # בדיקה: אחרי wait ובצוע הזזה, selected_position מתאפס.
    def test_selection_cleared_after_wait_and_move(self):
        grid = [["wK", EMPTY_SQUARE]]
        game = make_game(grid)
        game.click(0, 0)
        game.click(100, 0)
        game.wait(1000)
        self.assertIsNone(game.selected_position)

    # בדיקה: תנועה לא חוקית — הכלי לא זז גם אחרי wait.
    def test_invalid_move_does_not_execute_after_wait(self):
        # מלך לא יכול לזוז שתי משבצות
        grid = [["wK", EMPTY_SQUARE, EMPTY_SQUARE]]
        game = make_game(grid)
        game.click(0, 0)
        game.click(200, 0)  # שתי משבצות — לא חוקי למלך
        game.wait(1000)
        self.assertEqual(game.board.get_piece(Position(0, 0)), "wK")

    # בדיקה: אכילת כלי יריב — אחרי wait, התוקף ביעד והמקור ריק.
    def test_capture_executes_after_wait(self):
        grid = [["wK", "bR"]]
        game = make_game(grid)
        game.click(0, 0)
        game.click(100, 0)
        game.wait(1000)
        self.assertEqual(game.board.get_piece(Position(0, 1)), "wK")
        self.assertEqual(game.board.get_piece(Position(0, 0)), EMPTY_SQUARE)


# ---------------------------------------------------------------------------
# בדיקות Game — wait
# ---------------------------------------------------------------------------

class TestGameWait(unittest.TestCase):

    # בדיקה: wait מקדם את שעון המשחק.
    def test_wait_advances_clock(self):
        grid = [["wK"]]
        game = make_game(grid)
        game.wait(300)
        self.assertEqual(game.clock.current_time, 300)

    # בדיקה: wait עם ערך שלילי זורק ValueError.
    def test_wait_negative_raises(self):
        grid = [["wK"]]
        game = make_game(grid)
        with self.assertRaises(ValueError):
            game.wait(-50)

    # בדיקה: wait ללא מהלך ממתין לא גורם לשגיאה.
    def test_wait_without_pending_move_is_safe(self):
        grid = [["wK"]]
        game = make_game(grid)
        game.wait(500)
        self.assertEqual(game.clock.current_time, 500)


if __name__ == "__main__":
    unittest.main()
