from model.piece import Piece, PieceColor, PieceType


class PieceCodeResolver:
    """
    Converts a logical chess piece into the corresponding
    asset folder name.

    Examples:
        White King   -> KW
        Black Pawn   -> PB
        White Knight -> NW
    """

    @staticmethod
    def resolve(piece: Piece) -> str:
        """
        Returns the asset folder code of the given piece.
        """

        piece_codes = {
            (PieceType.KING, PieceColor.WHITE): "KW",
            (PieceType.QUEEN, PieceColor.WHITE): "QW",
            (PieceType.ROOK, PieceColor.WHITE): "RW",
            (PieceType.BISHOP, PieceColor.WHITE): "BW",
            (PieceType.KNIGHT, PieceColor.WHITE): "NW",
            (PieceType.PAWN, PieceColor.WHITE): "PW",

            (PieceType.KING, PieceColor.BLACK): "KB",
            (PieceType.QUEEN, PieceColor.BLACK): "QB",
            (PieceType.ROOK, PieceColor.BLACK): "RB",
            (PieceType.BISHOP, PieceColor.BLACK): "BB",
            (PieceType.KNIGHT, PieceColor.BLACK): "NB",
            (PieceType.PAWN, PieceColor.BLACK): "PB",
        }

        return piece_codes[(piece.type, piece.color)]