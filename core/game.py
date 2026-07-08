# core/game.py
"""
מחלקת Game מנהלת את מצב המשחק בשחמט קונג-פו:
  - בחירת כלי (selected_position)
  - שמירת מהלך ממתין (pending_move) — מה שנבחר ב-click השני
  - ביצוע המהלך בפועל רק ב-wait() — אחרי שחלף הזמן הדרוש
  - קידום שעון המשחק
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
        self._pending_move = None  # (from_pos, to_pos, piece_code) ממתין לביצוע ב-wait

    def click(self, x, y):
        """
        מטפלת בלחיצה בקואורדינטות פיקסלים.
        ממירה לתא בלוח (כל תא = 100 פיקסלים) ומנתבת לפעולה המתאימה.
        """
        col = x // 100
        row = y // 100
        pos = Position(row, col)

        # לחיצה מחוץ ללוח — מתעלמים לגמרי
        if not self.board.is_inside(pos):
            return

        clicked_piece = self.board.get_piece(pos)

        if self.selected_position is None:
            self._handle_new_selection(pos, clicked_piece)
        else:
            self._handle_existing_selection(pos, clicked_piece)

    def _handle_new_selection(self, pos, clicked_piece):
        """בחירה ראשונית — בוחרים כלי רק אם המשבצת אינה ריקה."""
        if clicked_piece != Board.EMPTY_CELL:
            self.selected_position = pos

    def _handle_existing_selection(self, pos, clicked_piece):
        """
        כשכבר יש כלי נבחר:
          - לחיצה על כלי שלנו → מחליפים בחירה
          - לחיצה על ריק או כלי יריב → שומרים מהלך ממתין (לא מבצעים עדיין)
        """
        selected_piece = self.board.get_piece(self.selected_position)

        if self._is_same_color(selected_piece, clicked_piece):
            # לחצנו על כלי נוסף שלנו — מחליפים את הבחירה
            self.selected_position = pos
        else:
            # בודקים חוקיות ושומרים כמהלך ממתין
            self._queue_move(pos, selected_piece)

    def _is_same_color(self, piece1, piece2):
        """True אם שני הכלים שייכים לאותו שחקן. משבצת ריקה = לא אותו צבע."""
        if piece2 == Board.EMPTY_CELL:
            return False
        return piece1[0] == piece2[0]

    def _queue_move(self, target_pos, piece):
        """
        בודק חוקיות התנועה — אם חוקית, שומר אותה כ-pending.
        המהלך יתבצע בפועל רק ב-wait().
        """
        piece_obj = piece_from_code(piece)

        # כלי לא ממומש (למשל פיון ריק) — מבטלים בחירה
        if piece_obj is None:
            self.selected_position = None
            return

        if not piece_obj.can_move(self.selected_position, target_pos, self.board):
            # תנועה לא חוקית — מבטלים בחירה, לא שומרים מהלך
            self.selected_position = None
            return

        # תנועה חוקית — שומרים כממתין
        self._pending_move = (self.selected_position, target_pos, piece)
        self.selected_position = None

    def _execute_pending_move(self):
        """מבצע את המהלך הממתין על הלוח, אם קיים."""
        if self._pending_move is None:
            return

        from_pos, to_pos, piece = self._pending_move
        self.board.set_piece(to_pos, piece)
        self.board.set_piece(from_pos, Board.EMPTY_CELL)
        self._pending_move = None

    def wait(self, ms):
        """
        מקדם את שעון המשחק ב-ms מילישניות
        ומבצע את המהלך הממתין (אם קיים).
        """
        self.clock.tick(ms)
        self._execute_pending_move()
