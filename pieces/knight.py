# pieces/knight.py
"""
פרש — הכלי היחיד שקופץ מעל כלים אחרים.
תנועתו בצורת L: שתי משבצות בציר אחד ומשבצת אחת בציר הניצב.
"""

from pieces.piece import Piece


class Knight(Piece):

    def can_move(self, from_pos, to_pos):
        """
        חוקי תנועת פרש:
          אפשרויות L: (±2, ±1) או (±1, ±2)
          כלומר: מכפלת ההפרשים = 2  (אחד הפרש 1 והשני הפרש 2)
        """
        row_diff = abs(to_pos.row - from_pos.row)
        col_diff = abs(to_pos.column - from_pos.column)

        # תנועת L: ההפרשים הם בדיוק 1 ו-2 (בסדר כלשהו)
        return sorted([row_diff, col_diff]) == [1, 2]
