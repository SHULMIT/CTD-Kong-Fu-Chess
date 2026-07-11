"""
Factory responsible for creating Piece objects.
"""

from model.position import Position
from model.piece import Piece, PieceState


class PieceFactory:
    """
    Responsible for creating Piece objects.

    The factory does not parse board text.
    It only creates Piece instances from already parsed data.
    """

    _next_piece_id = 1

    @classmethod
    def create_piece(
        cls,
        piece_data,
        position: Position,
    ) -> Piece | None:
        """
        Creates a Piece object.

        Args:
            piece_data:
                Result returned by PieceMapper.from_code().
                None means the board cell is empty.
            position:
                Piece position on the board.

        Returns:
            Piece or None.
        """

        if piece_data is None:
            return None

        piece_type, color = piece_data

        piece = Piece(
            piece_id=cls._next_piece_id,
            piece_type=piece_type,
            color=color,
            position=position,
            state=PieceState.IDLE,
        )

        cls._next_piece_id += 1

        return piece