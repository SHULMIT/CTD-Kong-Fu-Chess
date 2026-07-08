# core/game.py

from core.position import Position
from core.board import Board
from core.clock import Clock

class Game:
    def __init__(self, board):
        self.board = board
        self.clock = Clock()
        self.selected_position = None

    def click(self, x, y):
        # המרת קואורדינטות פיקסלים למיקום בלוח
        col = x // 100
        row = y // 100
        pos = Position(row, col)

        # התעלמות מלחיצה מחוץ לגבולות הלוח
        if not self.board.is_inside(pos):
            return

        clicked_piece = self.board.get_piece(pos)

        # ניתוב הפעולה בהתאם למצב הבחירה הנוכחי
        if self.selected_position is None:
            self._handle_new_selection(pos, clicked_piece)
        else:
            self._handle_existing_selection(pos, clicked_piece)

    def _handle_new_selection(self, pos, clicked_piece):
        # מסמנים כלי רק אם המשבצת אינה ריקה
        if clicked_piece != Board.EMPTY_CELL:
            self.selected_position = pos

    def _handle_existing_selection(self, pos, clicked_piece):
        selected_piece = self.board.get_piece(self.selected_position)
        
        # אם לחצנו על כלי שלנו - מחליפים בחירה, אחרת זזים
        if self._is_same_color(selected_piece, clicked_piece):
            self.selected_position = pos
        else:
            self._move_piece(pos, selected_piece)

    def _is_same_color(self, piece1, piece2):
        # בדיקה האם שני הכלים שייכים לאותו שחקן
        if piece2 == Board.EMPTY_CELL:
            return False
        return piece1[0] == piece2[0]

    def _move_piece(self, target_pos, piece):
        # העברת הכלי ליעד וניקוי משבצת המקור
        self.board.set_piece(target_pos, piece)
        self.board.set_piece(self.selected_position, Board.EMPTY_CELL)
        self.selected_position = None

    def wait(self, ms):
        # קידום שעון המשחק
        self.clock.tick(ms)