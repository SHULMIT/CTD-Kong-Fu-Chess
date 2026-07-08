# pieces/bishop.py
"""
רץ — יכול לזוז כמה משבצות שרוצה, אבל רק באלכסון.
"""

from pieces.piece import Piece


class Bishop(Piece):

    def can_move(self, from_pos, to_pos):
        """
        חוקי תנועת רץ:
          - הפרש השורות חייב להיות שווה להפרש העמודות (אלכסון מושלם)
          - חייב לזוז (לא עומד במקום)
        """
        row_diff = abs(to_pos.row - from_pos.row)
        col_diff = abs(to_pos.column - from_pos.column)

        # אלכסון: שני הצירים משתנים באותה כמות
        return row_diff == col_diff and row_diff > 0
