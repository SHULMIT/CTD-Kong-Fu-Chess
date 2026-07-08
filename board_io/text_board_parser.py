# io/text_board_parser.py

from core.board import Board
from config.constants import EMPTY_SQUARE, VALID_COLORS, VALID_PIECES, ERR_UNKNOWN_TOKEN, ERR_ROW_WIDTH_MISMATCH

"""
    מחלקה זו מקבלת שורות טקסט, מוודאת את תקינותן (ולידציה) ומייצרת אובייקט Board. האחריות שלה היא פיענוח בלבד (SRP)
"""


class TextBoardParser:
    @staticmethod
    def _is_valid_token(token):
        if token == EMPTY_SQUARE:
            return True
        if len(token) == 2 and token[0] in VALID_COLORS and token[1] in VALID_PIECES:
            return True
        return False

    @staticmethod
    def parse(board_lines):
        if not board_lines:
            return Board([])

        grid = []
        expected_width = None

        for line in board_lines:
            tokens = line.strip().split()
            if not tokens:
                continue

            # בדיקת רוחב שורה עקבי
            if expected_width is None:
                expected_width = len(tokens)
            elif len(tokens) != expected_width:
                raise ValueError(ERR_ROW_WIDTH_MISMATCH)

            # בדיקת תקינות טוקנים (כלים)
            for token in tokens:
                if not TextBoardParser._is_valid_token(token):
                    raise ValueError(ERR_UNKNOWN_TOKEN)

            grid.append(tokens)

        return Board(grid)
