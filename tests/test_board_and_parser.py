import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.board import Board
from core.position import Position
import importlib.util

PARSER_PATH = PROJECT_ROOT / "io" / "text_board_parser.py"
FORMATTER_PATH = PROJECT_ROOT / "io" / "text_board_formatter.py"

spec_parser = importlib.util.spec_from_file_location("text_board_parser", PARSER_PATH)
text_board_parser = importlib.util.module_from_spec(spec_parser)
spec_parser.loader.exec_module(text_board_parser)
TextBoardParser = text_board_parser.TextBoardParser

spec_formatter = importlib.util.spec_from_file_location("text_board_formatter", FORMATTER_PATH)
text_board_formatter = importlib.util.module_from_spec(spec_formatter)
spec_formatter.loader.exec_module(text_board_formatter)
TextBoardFormatter = text_board_formatter.TextBoardFormatter

from config.constants import EMPTY_SQUARE


class TestBoardAndParser(unittest.TestCase):
    # בדיקה: הלוח צריך לשמור את המידות הנכונות.
    def test_board_dimensions(self):
        grid = [
            [EMPTY_SQUARE, "wP"],
            ["bR", EMPTY_SQUARE],
        ]
        board = Board(grid)

        self.assertEqual(board.height, 2)
        self.assertEqual(board.width, 2)

    # בדיקה: ניתן לקבל את הכלי הנכון לפי מיקום.
    def test_get_piece_at_position(self):
        grid = [
            [EMPTY_SQUARE, "wP"],
            ["bR", EMPTY_SQUARE],
        ]
        board = Board(grid)

        pos = Position(0, 1)
        self.assertEqual(board.get_piece(pos), "wP")

    # בדיקה: מיקום מחוץ ללוח אמור לזרוק שגיאה.
    def test_out_of_bounds_position_raises(self):
        grid = [[EMPTY_SQUARE]]
        board = Board(grid)

        pos = Position(1, 0)
        with self.assertRaises(IndexError):
            board.get_piece(pos)

    # בדיקה: הפרשן צריך לזהות לוח תקין ולהחזיר אובייקט Board.
    def test_parser_accepts_valid_board_lines(self):
        board_lines = [". wP", "bR ."]
        board = TextBoardParser.parse(board_lines)

        self.assertIsInstance(board, Board)
        self.assertEqual(board.get_piece(Position(0, 1)), "wP")
        self.assertEqual(board.get_piece(Position(1, 0)), "bR")

    # בדיקה: הפרשן צריך לסרב לשורות שרוחבן שונה.
    def test_parser_rejects_mismatched_row_width(self):
        board_lines = [". wP", "bR"]

        with self.assertRaises(ValueError):
            TextBoardParser.parse(board_lines)

    # בדיקה: הפרשן צריך לסרב לסימנים לא מוכרים.
    def test_parser_rejects_unknown_token(self):
        board_lines = [". xx"]

        with self.assertRaises(ValueError):
            TextBoardParser.parse(board_lines)

    # בדיקה: הפורמט צריך להפיק טקסט תצוגה נכון מהלוח.
    def test_formatter_outputs_expected_text(self):
        grid = [
            [EMPTY_SQUARE, "wP"],
            ["bR", EMPTY_SQUARE],
        ]
        board = Board(grid)

        output = TextBoardFormatter.format(board)
        self.assertEqual(output, ". wP\nbR .")


if __name__ == "__main__":
    unittest.main()
