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
    """Represents the two piece colors.

    מייצגת את רכיב השרת ``PieceColor`` ומרכזת את התנהגותו.

    Responsibility: Represents the two piece colors.

    אחריות: מייצגת את רכיב השרת ``PieceColor`` ומרכזת את התנהגותו."""

    WHITE = auto()
    BLACK = auto()


class PieceType(Enum):
    """Represents all supported chess piece types.

    מייצגת את רכיב השרת ``PieceType`` ומרכזת את התנהגותו.

    Responsibility: Represents all supported chess piece types.

    אחריות: מייצגת את רכיב השרת ``PieceType`` ומרכזת את התנהגותו."""

    KING = auto()
    QUEEN = auto()
    ROOK = auto()
    BISHOP = auto()
    KNIGHT = auto()
    PAWN = auto()


class PieceState(Enum):
    """Represents the current life-cycle state of a piece.

    מייצגת את רכיב השרת ``PieceState`` ומרכזת את התנהגותו.

    Responsibility: Represents the current life-cycle state of a piece.

    אחריות: מייצגת את רכיב השרת ``PieceState`` ומרכזת את התנהגותו."""

    IDLE = auto()
    MOVING = auto()
    CAPTURED = auto()
    AIRBORNE = auto()



class Piece:
    """Represents a logical chess piece.

        Responsibilities:
            - Store the piece identity.
            - Store the piece type.
            - Store the piece color.
            - Store the current board position.
            - Store the current life-cycle state.

        This class does NOT contain movement rules.

    מייצגת את רכיב השרת ``Piece`` ומרכזת את התנהגותו.

    Responsibility: Represents a logical chess piece.

    אחריות: מייצגת את רכיב השרת ``Piece`` ומרכזת את התנהגותו."""

    def __init__(
        self,
        piece_id: int,
        piece_type: PieceType,
        color: PieceColor,
        position: Position,
        state: PieceState = PieceState.IDLE,
    ):
        """Initialize the instance and its dependencies.

        מאתחלת את המופע ואת התלויות שלו."""
        self._id = piece_id
        self._type = piece_type
        self._color = color
        self._position = position
        self._state = state

    @property
    def id(self) -> int:
        """Perform the id operation.

        מבצעת את פעולת המזהה."""
        return self._id

    @property
    def type(self) -> PieceType:
        """Perform the type operation.

        מבצעת את פעולת ``type``."""
        return self._type

    @property
    def color(self) -> PieceColor:
        """Perform the color operation.

        מבצעת את פעולת צבע."""
        return self._color

    @property
    def position(self) -> Position:
        """Perform the position operation.

        מבצעת את פעולת המיקום."""
        return self._position

    @property
    def state(self) -> PieceState:
        """Perform the state operation.

        מבצעת את פעולת המצב."""
        return self._state

    @position.setter
    def position(self, new_position: Position):
        """Perform the position operation.

        מבצעת את פעולת המיקום."""
        self._position = new_position

    @state.setter
    def state(self, new_state: PieceState):
        """Perform the state operation.

        מבצעת את פעולת המצב."""
        self._state = new_state

    @type.setter
    def type(
        self,
        new_type: PieceType,
    ) -> None:
        """Perform the type operation.

        מבצעת את פעולת ``type``."""
        self._type = new_type    

    def __repr__(self):
        """Return a developer-facing string representation.

        מחזירה ייצוג טקסטואלי המיועד למפתחים."""
        return (
            f"Piece("
            f"id={self._id}, "
            f"type={self._type.name}, "
            f"color={self._color.name}, "
            f"position={self._position}, "
            f"state={self._state.name})"
        )