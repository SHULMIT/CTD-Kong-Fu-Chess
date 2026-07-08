# pieces/piece.py
"""
מחלקה אבסטרקטית שמייצגת כלי שחמט כלשהו.
כל כלי קונקרטי (מלך, רץ, צריח...) יורש ממנה ומממש את can_move.

עיקרון העיצוב: Open/Closed —
  אפשר להוסיף כלי חדש (פיל, וזיר...) בלי לגעת בקוד הקיים.

כאן גם מוגדרת piece_from_code — פונקציית factory שממירה קוד טקסטואלי
("wK", "bR" וכו') לאובייקט Piece המתאים.
"""

from abc import ABC, abstractmethod


def _path_is_clear(from_pos, to_pos, board):
    """
    Returns True if all squares strictly between from_pos and to_pos are empty.
    Assumes the move is already known to be a straight line or diagonal.
    Works for both sliding pieces (Rook, Bishop, Queen).
    """
    from core.position import Position

    row_step = 0 if to_pos.row == from_pos.row else (1 if to_pos.row > from_pos.row else -1)
    col_step = 0 if to_pos.column == from_pos.column else (1 if to_pos.column > from_pos.column else -1)

    r = from_pos.row + row_step
    c = from_pos.column + col_step

    while (r, c) != (to_pos.row, to_pos.column):
        if board.get_piece(Position(r, c)) != board.EMPTY_CELL:
            return False
        r += row_step
        c += col_step

    return True


def _is_friendly_capture(from_pos, to_pos, board):
    """Returns True if the target square holds a friendly piece (same color)."""
    target = board.get_piece(to_pos)
    if target == board.EMPTY_CELL:
        return False
    moving = board.get_piece(from_pos)
    return target[0] == moving[0]


class Piece(ABC):
    """
    בסיס לכל הכלים.
    can_move מגדיר אם תנועה מ-from_pos אל to_pos חוקית עבור כלי זה.
    """

    @abstractmethod
    def can_move(self, from_pos, to_pos, board):
        """
        Returns True if moving from from_pos to to_pos is legal for this piece.
        Responsibilities:
          - movement shape (always)
          - path blocking — no piece may be jumped (sliding pieces only)
          - friendly capture prevention — cannot land on a square occupied by own color
        The board parameter gives access to piece positions for blocking/capture checks.
        """
        pass


def piece_from_code(code):
    """
    Factory: ממירה קוד כלי (כגון "wK", "bR") לאובייקט Piece המתאים.

    הייבוא מתבצע כאן (בתוך הפונקציה) כדי למנוע ייבוא מעגלי —
    כל קובץ כלי מייבא את Piece, ואם Piece היה מייבא אותם ברמת המודול
    היינו מקבלים תלות מעגלית.

    מחזירה None אם הקוד הוא משבצת ריקה או לא מוכר.
    """
    # ייבוא מקומי למניעת ייבוא מעגלי
    from pieces.king import King
    from pieces.rook import Rook
    from pieces.bishop import Bishop
    from pieces.queen import Queen
    from pieces.knight import Knight
    from pieces.pawn import Pawn

    # קוד תקין הוא באורך 2: צבע + סוג (למשל "wK")
    if len(code) != 2:
        return None

    color = code[0]       # האות הראשונה = צבע
    piece_letter = code[1]  # האות השנייה = סוג הכלי

    # פיון מקבל צבע כי כיוון התנועה שלו תלוי בצבע
    if piece_letter == 'P':
        return Pawn(color)

    # מיפוי: האות השנייה בקוד (סוג הכלי) → מחלקה
    PIECE_MAP = {
        'K': King,
        'R': Rook,
        'B': Bishop,
        'Q': Queen,
        'N': Knight,
    }

    piece_class = PIECE_MAP.get(piece_letter)

    if piece_class is None:
        return None

    return piece_class()
