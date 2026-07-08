import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.board import Board
from core.game import Game
from core.position import Position
from board_io.text_board_parser import TextBoardParser
from board_io.text_board_formatter import TextBoardFormatter
from config.constants import EMPTY_SQUARE


def make_board(grid):
    return Board([row[:] for row in grid])


def make_game(grid):
    return Game(make_board(grid))


# ---------------------------------------------------------------------------
# בדיקות Position
# ---------------------------------------------------------------------------

class TestPosition(unittest.TestCase):

    # בדיקה: שני מיקומים עם אותן קואורדינטות שווים זה לזה.
    def test_equal_positions_are_equal(self):
        self.assertEqual(Position(2, 3), Position(2, 3))

    # בדיקה: מיקומים עם קואורדינטות שונות אינם שווים.
    def test_different_positions_are_not_equal(self):
        self.assertNotEqual(Position(0, 1), Position(1, 0))

    # בדיקה: השוואה למשהו שאינו Position מחזירה False ולא זורקת שגיאה.
    def test_position_not_equal_to_non_position(self):
        self.assertNotEqual(Position(0, 0), "not a position")

    # בדיקה: __str__ מחזיר את הפורמט הצפוי.
    def test_str_format(self):
        self.assertEqual(str(Position(1, 4)), "(1, 4)")


# ---------------------------------------------------------------------------
# בדיקות Board — set_piece ו-is_inside
# ---------------------------------------------------------------------------

class TestBoardSetPiece(unittest.TestCase):

    # בדיקה: set_piece מעדכן את הכלי במיקום הנכון.
    def test_set_piece_updates_value(self):
        board = make_board([[EMPTY_SQUARE, EMPTY_SQUARE]])
        board.set_piece(Position(0, 1), "wQ")
        self.assertEqual(board.get_piece(Position(0, 1)), "wQ")

    # בדיקה: set_piece מחוץ לגבולות זורק IndexError.
    def test_set_piece_out_of_bounds_raises(self):
        board = make_board([[EMPTY_SQUARE]])
        with self.assertRaises(IndexError):
            board.set_piece(Position(5, 5), "wK")

    # בדיקה: set_piece לא פוגע בשאר הלוח.
    def test_set_piece_does_not_affect_other_cells(self):
        board = make_board([["wP", "bR"]])
        board.set_piece(Position(0, 0), "wQ")
        self.assertEqual(board.get_piece(Position(0, 1)), "bR")


class TestBoardIsInside(unittest.TestCase):

    # בדיקה: מיקום בתוך הלוח מוכר כחוקי.
    def test_inside_position_returns_true(self):
        board = make_board([["wP", "bR"], [EMPTY_SQUARE, "wK"]])
        self.assertTrue(board.is_inside(Position(1, 1)))

    # בדיקה: שורה שלילית מחוץ לגבולות.
    def test_negative_row_returns_false(self):
        board = make_board([["wP"]])
        self.assertFalse(board.is_inside(Position(-1, 0)))

    # בדיקה: עמודה שלילית מחוץ לגבולות.
    def test_negative_column_returns_false(self):
        board = make_board([["wP"]])
        self.assertFalse(board.is_inside(Position(0, -1)))

    # בדיקה: שורה בדיוק בגבול העליון (height) מחוץ לגבולות.
    def test_row_equals_height_returns_false(self):
        board = make_board([["wP"], ["bR"]])
        self.assertFalse(board.is_inside(Position(2, 0)))

    # בדיקה: עמודה בדיוק בגבול הימני (width) מחוץ לגבולות.
    def test_column_equals_width_returns_false(self):
        board = make_board([["wP", "bR"]])
        self.assertFalse(board.is_inside(Position(0, 2)))


# ---------------------------------------------------------------------------
# בדיקות Board — לוח ריק
# ---------------------------------------------------------------------------

class TestEmptyBoard(unittest.TestCase):

    # בדיקה: לוח ריק (ללא שורות) מחזיר גובה ורוחב אפס.
    def test_empty_board_dimensions(self):
        board = Board([])
        self.assertEqual(board.height, 0)
        self.assertEqual(board.width, 0)

    # בדיקה: is_inside על לוח ריק תמיד מחזיר False.
    def test_empty_board_is_inside_returns_false(self):
        board = Board([])
        self.assertFalse(board.is_inside(Position(0, 0)))


# ---------------------------------------------------------------------------
# בדיקות TextBoardParser — מקרי קצה
# ---------------------------------------------------------------------------

class TestParserEdgeCases(unittest.TestCase):

    # בדיקה: קלט ריק מחזיר לוח ריק.
    def test_parse_empty_input_returns_empty_board(self):
        board = TextBoardParser.parse([])
        self.assertEqual(board.height, 0)

    # בדיקה: הפרשן מזהה את כל סוגי הכלים החוקיים.
    def test_parser_accepts_all_valid_piece_types(self):
        board_lines = ["wK wQ wR wB wN wP"]
        board = TextBoardParser.parse(board_lines)
        self.assertEqual(board.get_piece(Position(0, 0)), "wK")
        self.assertEqual(board.get_piece(Position(0, 5)), "wP")

    # בדיקה: הפרשן מזהה כלים שחורים.
    def test_parser_accepts_black_pieces(self):
        board_lines = ["bK bQ bR bB bN bP"]
        board = TextBoardParser.parse(board_lines)
        self.assertEqual(board.get_piece(Position(0, 0)), "bK")

    # בדיקה: הפרשן מתעלם משורות ריקות.
    def test_parser_skips_blank_lines(self):
        board_lines = ["wP .", "", "bR ."]
        board = TextBoardParser.parse(board_lines)
        self.assertEqual(board.height, 2)

    # בדיקה: לוח עם משבצת אחת בלבד (1x1) תקין.
    def test_parser_accepts_single_cell_board(self):
        board = TextBoardParser.parse(["wK"])
        self.assertEqual(board.height, 1)
        self.assertEqual(board.width, 1)
        self.assertEqual(board.get_piece(Position(0, 0)), "wK")

    # בדיקה: רצף אותיות שלא תואם לפורמט צבע+כלי נדחה.
    def test_parser_rejects_piece_with_wrong_color(self):
        with self.assertRaises(ValueError):
            TextBoardParser.parse(["xP"])

    # בדיקה: אות בודדת (לא נקודה) נדחית.
    def test_parser_rejects_single_letter(self):
        with self.assertRaises(ValueError):
            TextBoardParser.parse(["w"])

    # בדיקה: token בן שלוש אותיות נדחה.
    def test_parser_rejects_three_char_token(self):
        with self.assertRaises(ValueError):
            TextBoardParser.parse(["wPP"])


# ---------------------------------------------------------------------------
# בדיקות TextBoardFormatter — מקרי קצה
# ---------------------------------------------------------------------------

class TestFormatterEdgeCases(unittest.TestCase):

    # בדיקה: לוח שורה אחת מפורמט נכון.
    def test_format_single_row(self):
        board = make_board([["wP", EMPTY_SQUARE, "bR"]])
        self.assertEqual(TextBoardFormatter.format(board), "wP . bR")

    # בדיקה: לוח 3x3 עם שורות מרובות.
    def test_format_multiple_rows(self):
        board = make_board([
            ["wR", EMPTY_SQUARE, "wR"],
            [EMPTY_SQUARE, "wK", EMPTY_SQUARE],
            ["bR", EMPTY_SQUARE, "bR"],
        ])
        expected = "wR . wR\n. wK .\nbR . bR"
        self.assertEqual(TextBoardFormatter.format(board), expected)

    # בדיקה: parse ואז format מחזירים את הקלט המקורי (round-trip).
    def test_format_after_parse_round_trip(self):
        original = ". wP\nbR ."
        board = TextBoardParser.parse(original.splitlines())
        self.assertEqual(TextBoardFormatter.format(board), original)


# ---------------------------------------------------------------------------
# בדיקות Game — מקרי קצה נוספים
# ---------------------------------------------------------------------------

class TestGameEdgeCases(unittest.TestCase):

    # בדיקה: לחיצה כפולה על אותו כלי — נשאר נבחר (לא מתבטל).
    def test_click_same_piece_twice_keeps_selection(self):
        grid = [["wK", EMPTY_SQUARE]]
        game = make_game(grid)
        game.click(0, 0)
        game.click(0, 0)
        self.assertEqual(game.selected_position, Position(0, 0))

    # בדיקה: wait מצטבר ממספר קריאות.
    def test_wait_accumulates_across_calls(self):
        grid = [["wP"]]
        game = make_game(grid)
        game.wait(100)
        game.wait(200)
        game.wait(50)
        self.assertEqual(game.clock.current_time, 350)

    # בדיקה: לחיצה על ריק כשאין בחירה פעילה — שעון לא מושפע.
    def test_click_empty_without_selection_does_not_affect_clock(self):
        grid = [[EMPTY_SQUARE]]
        game = make_game(grid)
        game.click(0, 0)
        self.assertEqual(game.clock.current_time, 0)

    # בדיקה: הזזת כלי לא מוחקת כלים אחרים בלוח.
    def test_move_does_not_disturb_other_pieces(self):
        grid = [["wK", EMPTY_SQUARE, "bR"]]
        game = make_game(grid)
        game.click(0, 0)    # בוחרת wK
        game.click(100, 0)  # זזה ימינה (חוקי למלך — משבצת אחת)
        game.wait(1000)
        self.assertEqual(game.board.get_piece(Position(0, 2)), "bR")

    # בדיקה: לאחר אכילת כלי יריב, הלוח מכיל את הכלי התוקף במיקום היעד.
    def test_after_capture_attacker_is_at_target(self):
        grid = [["wK", "bR"]]
        game = make_game(grid)
        game.click(0, 0)
        game.click(100, 0)
        game.wait(1000)
        self.assertEqual(game.board.get_piece(Position(0, 1)), "wK")

    # בדיקה: לאחר אכילת כלי יריב, מיקום המקור הופך ריק.
    def test_after_capture_source_is_empty(self):
        grid = [["wK", "bR"]]
        game = make_game(grid)
        game.click(0, 0)
        game.click(100, 0)
        game.wait(1000)
        self.assertEqual(game.board.get_piece(Position(0, 0)), EMPTY_SQUARE)


if __name__ == "__main__":
    unittest.main()
