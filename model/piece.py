"""
piece.py

Contains the Piece entity and all enums related to chess pieces.

The Piece class belongs to the model layer and stores only the
logical state of a chess piece.

Movement logic is implemented in the rules package.
"""

from enum import Enum, auto

from model.position import Position


class PieceColor(Enum):
    """Represents the two piece colors."""

    WHITE = auto()
    BLACK = auto()


class PieceType(Enum):
    """Represents all supported chess piece types."""

    KING = auto()
    QUEEN = auto()
    ROOK = auto()
    BISHOP = auto()
    KNIGHT = auto()
    PAWN = auto()


class PieceState(Enum):
    """Represents the current life-cycle state of a piece."""

    IDLE = auto()
    MOVING = auto()
    CAPTURED = auto()
    AIRBORNE = auto()



class Piece:
    """
    Represents a logical chess piece.

    Responsibilities:
        - Store the piece identity.
        - Store the piece type.
        - Store the piece color.
        - Store the current board position.
        - Store the current life-cycle state.

    This class does NOT contain movement rules.
    """

    def __init__(
        self,
        piece_id: int,
        piece_type: PieceType,
        color: PieceColor,
        position: Position,
        state: PieceState = PieceState.IDLE,
    ):
        self._id = piece_id
        self._type = piece_type
        self._color = color
        self._position = position
        self._state = state

    @property
    def id(self) -> int:
        return self._id

    @property
    def type(self) -> PieceType:
        return self._type

    @property
    def color(self) -> PieceColor:
        return self._color

    @property
    def position(self) -> Position:
        return self._position

    @property
    def state(self) -> PieceState:
        return self._state

    @position.setter
    def position(self, new_position: Position):
        self._position = new_position

    @state.setter
    def state(self, new_state: PieceState):
        self._state = new_state

    @type.setter
    def type(
        self,
        new_type: PieceType,
    ) -> None:
        self._type = new_type    

    def __repr__(self):
        return (
            f"Piece("
            f"id={self._id}, "
            f"type={self._type.name}, "
            f"color={self._color.name}, "
            f"position={self._position}, "
            f"state={self._state.name})"
        )