# core/game.py
"""
מחלקת Game מנהלת את מצב המשחק:
  - בחירת כלי (selected_position)
  - ביצוע מהלך — בתנאי שהוא חוקי לפי סוג הכלי
  - קידום שעון המשחק

שינוי מהאיטרציה הקודמת:
  _move_piece עכשיו בודק חוקיות תנועה באמצעות piece_from_code לפני
  שהוא מבצע את ההזזה. אם התנועה אסורה — הלוח לא משתנה.
"""

from core.position import Position
from core.board import Board
from core.clock import Clock
from pieces.piece import piece_from_code


class Game:
    def __init__(self, board):
        self.board = board
        self.clock = Clock()
        self.selected_position = None

    def click(self, x, y):
        """
        מטפלת בלחיצה בקואורדינטות פיקסלים.
        ממירה לתא בלוח (כל תא = 100 פיקסלים) ומנתבת לפעולה המתאימה.
        """
        # המרת קואורדינטות פיקסלים לאינדקסים בלוח (כל תא 100 פיקסלים)
        col = x // 100
        row = y // 100
        pos = Position(row, col)

        # לחיצה מחוץ ללוח — מתעלמים לגמרי
        if not self.board.is_inside(pos):
            return

        clicked_piece = self.board.get_piece(pos)

        # ניתוב: אם אין בחירה פעילה — מנסים לבחור; אחרת — מנסים לזוז
        if self.selected_position is None:
            self._handle_new_selection(pos, clicked_piece)
        else:
            self._handle_existing_selection(pos, clicked_piece)

    def _handle_new_selection(self, pos, clicked_piece):
        """
        בחירה ראשונית — בוחרים כלי רק אם המשבצת אינה ריקה.
        """
        if clicked_piece != Board.EMPTY_CELL:
            self.selected_position = pos

    def _handle_existing_selection(self, pos, clicked_piece):
        """
        כשכבר יש כלי נבחר:
          - לחיצה על כלי שלנו → מחליפים בחירה
          - לחיצה על ריק או כלי יריב → מנסים לזוז (בכפוף לחוקיות)
        """
        selected_piece = self.board.get_piece(self.selected_position)

        if self._is_same_color(selected_piece, clicked_piece):
            # לחצנו על כלי נוסף שלנו — מחליפים את הבחירה
            self.selected_position = pos
        else:
            # מנסים לבצע מהלך — תתבצע רק אם חוקית לפי סוג הכלי
            self._move_piece(pos, selected_piece)

    def _is_same_color(self, piece1, piece2):
        """
        מחזיר True אם שני הכלים שייכים לאותו שחקן (אותה אות ראשונה).
        משבצת ריקה נחשבת תמיד כ"לא אותו צבע".
        """
        if piece2 == Board.EMPTY_CELL:
            return False
        return piece1[0] == piece2[0]

    def _move_piece(self, target_pos, piece):
        """
        מבצע את ההזזה רק אם התנועה חוקית לפי סוג הכלי.

        תהליך:
          1. מקבלים אובייקט Piece מתאים דרך piece_from_code
          2. שואלים אותו: can_move(from, to)?
          3. רק אם כן — מבצעים את ההזזה בפועל על הלוח
        """
        # יוצרים את אובייקט הכלי המתאים לפי קוד הטקסט (למשל "wK" → King)
        piece_obj = piece_from_code(piece)

        # אם הקוד לא מוכר (למשל כלי לא ממומש) — לא מזיזים
        if piece_obj is None:
            return

        # בודקים אם התנועה חוקית לפי חוקי הכלי הספציפי
        if not piece_obj.can_move(self.selected_position, target_pos):
            # תנועה לא חוקית — מבטלים את הבחירה ומחכים ללחיצה חדשה
            self.selected_position = None
            return

        # התנועה חוקית — מבצעים את ההזזה על הלוח
        self.board.set_piece(target_pos, piece)
        self.board.set_piece(self.selected_position, Board.EMPTY_CELL)
        self.selected_position = None

    def wait(self, ms):
        """
        מקדם את שעון המשחק ב-ms מילישניות.
        """
        self.clock.tick(ms)
