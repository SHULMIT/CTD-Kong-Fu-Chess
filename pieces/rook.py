# pieces/rook.py
"""
צריח — יכול לזוז כמה משבצות שרוצה, אבל רק בקו ישר (אופקי או אנכי).
"""

from pieces.piece import Piece


class Rook(Piece):

    def can_move(self, from_pos, to_pos):
        """
        חוקי תנועת צריח:
          - תנועה אופקית: שורה זהה, עמודה שונה
          - תנועה אנכית: עמודה זהה, שורה שונה
          - אלכסון — אסור (גם אם שורה וגם עמודה משתנות)
        """
        moved_row = from_pos.row != to_pos.row
        moved_col = from_pos.column != to_pos.column

        # חוקי רק אם זז בציר אחד בלבד
        return moved_row != moved_col  # XOR — בדיוק אחד מהם
