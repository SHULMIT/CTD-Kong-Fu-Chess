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


class Piece(ABC):
    """
    בסיס לכל הכלים.
    can_move מגדיר אם תנועה מ-from_pos אל to_pos חוקית עבור כלי זה.
    """

    @abstractmethod
    def can_move(self, from_pos, to_pos):
        """
        מקבלת שני אובייקטי Position ומחזירה True אם התנועה חוקית.
        אחריות: בדיקת צורת התנועה בלבד — לא בדיקת גבולות לוח.
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

    # מיפוי: האות השנייה בקוד (סוג הכלי) → מחלקה
    PIECE_MAP = {
        'K': King,
        'R': Rook,
        'B': Bishop,
        'Q': Queen,
        'N': Knight,
    }

    # קוד תקין הוא באורך 2: צבע + סוג (למשל "wK")
    if len(code) != 2:
        return None

    piece_letter = code[1]  # האות השנייה = סוג הכלי
    piece_class = PIECE_MAP.get(piece_letter)

    if piece_class is None:
        return None

    return piece_class()
