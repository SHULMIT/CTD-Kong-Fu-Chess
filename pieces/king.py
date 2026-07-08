# pieces/king.py
"""
מלך — יכול לזוז בדיוק משבצת אחת בכל כיוון (אופקי, אנכי, אלכסוני).
"""

from pieces.piece import Piece


class King(Piece):

    def can_move(self, from_pos, to_pos):
        """
        חוקי תנועת מלך:
          - הפרש השורות בין 0 ל-1 (לא יותר משורה אחת)
          - הפרש העמודות בין 0 ל-1 (לא יותר מעמודה אחת)
          - לא עומד במקום (חייב לזוז לפחות משבצת אחת)
        """
        row_diff = abs(to_pos.row - from_pos.row)
        col_diff = abs(to_pos.column - from_pos.column)

        # חייב לזוז, ולכל היותר משבצת אחת בכל ציר
        return max(row_diff, col_diff) == 1
