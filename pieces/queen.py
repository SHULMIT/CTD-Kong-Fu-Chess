# pieces/queen.py
"""
מלכה — משלבת את יכולות הצריח והרץ:
  יכולה לזוז בקו ישר (אופקי/אנכי) או באלכסון, כמה משבצות שרוצה.
"""

from pieces.piece import Piece
from pieces.rook import Rook
from pieces.bishop import Bishop


class Queen(Piece):

    def __init__(self):
        # מלכה = צריח + רץ, משתמשים בהם ישירות
        self._rook = Rook()
        self._bishop = Bishop()

    def can_move(self, from_pos, to_pos):
        """
        תנועה חוקית אם חוקית לצריח OR חוקית לרץ.
        """
        return (
            self._rook.can_move(from_pos, to_pos)
            or
            self._bishop.can_move(from_pos, to_pos)
        )
