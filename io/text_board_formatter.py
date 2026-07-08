# io/text_board_formatter.py

from core.board import Board
from core.position import Position


class TextBoardFormatter:
    @staticmethod
    def format(board):
        lines = []
        for row in range(board.height):
            line_tokens = []
            for col in range(board.width):
                pos = Position(row, col)
                line_tokens.append(board.get_piece(pos))
            lines.append(" ".join(line_tokens))
        return "\n".join(lines)