# io/text_board_formatter.py

from core.board import Board

class TextBoardFormatter:
    @staticmethod
    def format(board: Board) -> str:
        lines = []
        for row in range(board.height):
            line_tokens = []
            for col in range(board.width):
                line_tokens.append(board.get_piece_at(row, col))
            lines.append(" ".join(line_tokens))
        return "\n".join(lines)