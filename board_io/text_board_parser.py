from config.constants import (
    EMPTY_SQUARE,
    VALID_COLORS,
    VALID_PIECES,
    ERR_UNKNOWN_TOKEN,
    ERR_ROW_WIDTH_MISMATCH,
)

from model.board import Board
from model.position import Position
from model.piece_factory import PieceFactory
from model.piece_mapper import PieceMapper


class TextBoardParser:
    """
    Parses a textual board representation into a Board object.

    Responsibilities:
        - Validate the input.
        - Convert text tokens into Piece objects.
        - Build the Board.
    """

    @staticmethod
    def _is_valid_token(token: str) -> bool:
        """
        Returns True if the given token is a valid board cell.
        """

        if token == EMPTY_SQUARE:
            return True

        return (
            len(token) == 2
            and token[0] in VALID_COLORS
            and token[1] in VALID_PIECES
        )

    @staticmethod
    def parse(board_lines: list[str]) -> Board:
        """
        Creates a Board from its textual representation.
        """

        if not board_lines:
            return Board([])

        grid = []
        expected_width = None

        for row, line in enumerate(board_lines):

            tokens = line.strip().split()

            if not tokens:
                continue

            if expected_width is None:
                expected_width = len(tokens)

            elif len(tokens) != expected_width:
                raise ValueError(ERR_ROW_WIDTH_MISMATCH)

            board_row = []

            for column, token in enumerate(tokens):

                if not TextBoardParser._is_valid_token(token):
                    raise ValueError(ERR_UNKNOWN_TOKEN)

                position = Position(row, column)

                piece_data = PieceMapper.from_code(token)

                piece = PieceFactory.create_piece(
                    piece_data=piece_data,
                    position=position,
                )

                board_row.append(piece)

            grid.append(board_row)

        return Board(grid)