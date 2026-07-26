"""
Converts between board text representation and piece data.
"""

from config.constants import EMPTY_SQUARE
from model.piece import Piece, PieceColor, PieceType


PIECE_COLOR_FROM_CODE = {
    "w": PieceColor.WHITE,
    "b": PieceColor.BLACK,
}

PIECE_CODE_FROM_COLOR = {
    PieceColor.WHITE: "w",
    PieceColor.BLACK: "b",
}

PIECE_TYPE_FROM_CODE = {
    "K": PieceType.KING,
    "Q": PieceType.QUEEN,
    "R": PieceType.ROOK,
    "B": PieceType.BISHOP,
    "N": PieceType.KNIGHT,
    "P": PieceType.PAWN,
}

PIECE_CODE_FROM_TYPE = {
    PieceType.KING: "K",
    PieceType.QUEEN: "Q",
    PieceType.ROOK: "R",
    PieceType.BISHOP: "B",
    PieceType.KNIGHT: "N",
    PieceType.PAWN: "P",
}


class PieceMapper:
    """Converts between textual board codes and Piece information.

    מייצגת את רכיב השרת ``PieceMapper`` ומרכזת את התנהגותו.

    Responsibility: Converts between textual board codes and Piece information.

    אחריות: מייצגת את רכיב השרת ``PieceMapper`` ומרכזת את התנהגותו."""

    @staticmethod
    def color_from_code(code: str) -> PieceColor:
        """Converts 'w' or 'b' into PieceColor.

        מבצעת את פעולת צבע ``from`` ``code``."""
        return PIECE_COLOR_FROM_CODE[code]

    @staticmethod
    def type_from_code(code: str) -> PieceType:
        """Converts 'P', 'R', ... into PieceType.

        מבצעת את פעולת ``type`` ``from`` ``code``."""
        return PIECE_TYPE_FROM_CODE[code]

    @staticmethod
    def from_code(code: str) -> tuple[PieceType, PieceColor] | None:
        """Converts a textual board token like 'wP' into piece metadata.

        מבצעת את פעולת ``from`` ``code``."""
        if code == EMPTY_SQUARE:
            return None

        return (
            PIECE_TYPE_FROM_CODE[code[1]],
            PIECE_COLOR_FROM_CODE[code[0]],
        )

    @staticmethod
    def to_code(piece: Piece | None) -> str:
        """Converts a Piece into its board representation.

        מבצעת את פעולת ``to`` ``code``."""

        if piece is None or piece == EMPTY_SQUARE:
            return EMPTY_SQUARE

        return (
            PIECE_CODE_FROM_COLOR[piece.color]
            + PIECE_CODE_FROM_TYPE[piece.type]
        )