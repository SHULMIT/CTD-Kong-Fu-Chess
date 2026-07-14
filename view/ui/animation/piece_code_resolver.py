from model.piece import Piece


class PieceCodeResolver:
    """Maps a model piece to the code used by the sprite folders."""

    @staticmethod
    def resolve(piece: Piece) -> str:
        color = "W" if piece.color.name == "WHITE" else "B"
        piece_letter = {
            "KING": "K",
            "QUEEN": "Q",
            "ROOK": "R",
            "BISHOP": "B",
            "KNIGHT": "N",
            "PAWN": "P",
        }[piece.type.name]
        return f"{piece_letter}{color}"
