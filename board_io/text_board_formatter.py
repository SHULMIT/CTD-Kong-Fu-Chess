from model.board import Board
from model.position import Position
from model.piece_mapper import PieceMapper


class TextBoardFormatter:
    """
    Converts a Board object into its textual representation.
    """

    @staticmethod
    def format(board: Board) -> str:
        lines = []

        for row in range(board.height):
            line_tokens = []

            for column in range(board.width):
                position = Position(row, column)
                piece = board.get_piece(position)
                line_tokens.append(PieceMapper.to_code(piece))

            lines.append(" ".join(line_tokens))

        return "\n".join(lines)
