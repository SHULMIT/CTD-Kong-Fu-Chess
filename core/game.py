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


def _move_duration_ms(from_pos, to_pos):
    """Returns the time needed for a move based on the board distance."""
    distance = max(abs(to_pos.row - from_pos.row), abs(to_pos.column - from_pos.column))
    return distance * 1000


class Game:
    def __init__(self, board):
        self.board = board
        self.clock = Clock()
        self.selected_position = None
        self._pending_move = None  # (from_pos, to_pos, piece_code) ממתין להתחלה
        self._active_move = None  # {'from_pos':..., 'to_pos':..., 'piece':..., 'remaining_time_ms':...}
        self.game_over = False

    def _is_move_in_progress(self):
        """True while a piece is already traveling along its route."""
        return self._active_move is not None

    def click(self, x, y):
        """
        מטפלת בלחיצה בקואורדינטות פיקסלים.
        ממירה לתא בלוח (כל תא = 100 פיקסלים) ומנתבת לפעולה המתאימה.
        """
        if self.game_over or self._is_move_in_progress():
            return

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
        המהלך יתחיל רק כשהזמן יתקדם ב-wait().
        """
        piece_obj = piece_from_code(piece)

        if self._pending_move is not None:
            self.selected_position = None
            return

        # כלי לא ממומש (למשל פיון ריק) — מבטלים בחירה
        if piece_obj is None:
            self.selected_position = None
            return

        if not piece_obj.can_move(self.selected_position, target_pos, self.board):
            # תנועה לא חוקית — מבטלים בחירה, לא שומרים מהלך
            self.selected_position = None
            return

        # תנועה חוקית — שומרים כממתין להתחלה
        self._pending_move = (self.selected_position, target_pos, piece)
        self.selected_position = None

    def _start_pending_move(self):
        """Start a queued move and begin its elapsed-time tracking."""
        if self._pending_move is None:
            return

        from_pos, to_pos, piece = self._pending_move
        duration_ms = _move_duration_ms(from_pos, to_pos)
        self._active_move = {
            "from_pos": from_pos,
            "to_pos": to_pos,
            "piece": piece,
            "remaining_time_ms": duration_ms,
        }
        self._pending_move = None

    def _advance_active_move(self, ms):
        """Advance an in-progress move and apply it once its travel time is exhausted."""
        if self._active_move is None:
            return

        self._active_move["remaining_time_ms"] -= ms
        if self._active_move["remaining_time_ms"] <= 0:
            self._apply_move(
                self._active_move["from_pos"],
                self._active_move["to_pos"],
                self._active_move["piece"],
            )
            self._active_move = None

    def _apply_move(self, from_pos, to_pos, piece):
        """Apply a completed move to the board."""
        target_piece = self.board.get_piece(to_pos)
        self.board.set_piece(to_pos, piece)
        self.board.set_piece(from_pos, Board.EMPTY_CELL)

        if self._is_enemy_king_capture(piece, target_piece):
            self.game_over = True

    def _is_enemy_king_capture(self, moving_piece, target_piece):
        """True when the move lands on the opponent king."""
        if target_piece == Board.EMPTY_CELL or target_piece is None:
            return False
        if len(target_piece) != 2 or len(moving_piece) != 2:
            return False
        return target_piece[1] == 'K' and target_piece[0] != moving_piece[0]

    def wait(self, ms):
        """
        מקדם את שעון המשחק ב-ms מילישניות
        ומתקדם את התנועה הממתינה אם יש.
        """
        if ms < 0:
            raise ValueError("wait time cannot be negative")

        if self.game_over:
            return

        self.clock.tick(ms)

        if self._active_move is None and self._pending_move is not None:
            self._start_pending_move()

        if self._active_move is not None:
            self._advance_active_move(ms)
