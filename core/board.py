# core/board.py

class Board:
    def __init__(self, grid):
        self._grid = grid
        self.height = len(grid)
        self.width = len(grid[0]) if self.height > 0 else 0

    def get_piece_at(self, row, col):
        """מחזירה את הכלי במיקום המבוקש מבלי לחשוף את מבנה הנתונים הפנימי"""
        return self._grid[row][col]

    def get_piece(self, position):
        return self.get_piece_at(position.row, position.column)