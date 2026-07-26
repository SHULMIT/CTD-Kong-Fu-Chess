"""
Defines user-facing input errors for invalid commands and invalid interactions.
"""

from config.constants import (
    ERR_CLICK_EMPTY_SOURCE,
    ERR_CLICK_OUTSIDE_BOARD,
    ERR_EMPTY_COMMAND,
    ERR_EMPTY_SOURCE,
    ERR_FRIENDLY_DESTINATION,
    ERR_GAME_OVER,
    ERR_ILLEGAL_PIECE_MOVE,
    ERR_JUMP_EMPTY_SOURCE,
    ERR_JUMP_OUTSIDE_BOARD,
    ERR_MOTION_IN_PROGRESS,
    ERR_UNKNOWN_COMMAND,
)
from game.move_reason import MoveReason


class UserInputError(Exception):
    """Base error for invalid user input that should be shown to the user.

    מייצגת את רכיב השרת ``UserInputError`` ומרכזת את התנהגותו.

    Responsibility: Base error for invalid user input that should be shown to the user.

    אחריות: מייצגת את רכיב השרת ``UserInputError`` ומרכזת את התנהגותו."""


class EmptyCommandError(UserInputError):
    """Represent the server-side empty command error concept.

    מייצגת את רכיב השרת ``EmptyCommandError`` ומרכזת את התנהגותו.

    Responsibility: Represent the server-side empty command error concept.

    אחריות: מייצגת את רכיב השרת ``EmptyCommandError`` ומרכזת את התנהגותו."""
    def __init__(self):
        """Initialize the instance and its dependencies.

        מאתחלת את המופע ואת התלויות שלו."""
        super().__init__(ERR_EMPTY_COMMAND)


class UnknownCommandError(UserInputError):
    """Represent the server-side unknown command error concept.

    מייצגת את רכיב השרת ``UnknownCommandError`` ומרכזת את התנהגותו.

    Responsibility: Represent the server-side unknown command error concept.

    אחריות: מייצגת את רכיב השרת ``UnknownCommandError`` ומרכזת את התנהגותו."""
    def __init__(self):
        """Initialize the instance and its dependencies.

        מאתחלת את המופע ואת התלויות שלו."""
        super().__init__(ERR_UNKNOWN_COMMAND)


class ClickOutsideBoardError(UserInputError):
    """Represent the server-side click outside board error concept.

    מייצגת את רכיב השרת ``ClickOutsideBoardError`` ומרכזת את התנהגותו.

    Responsibility: Represent the server-side click outside board error concept.

    אחריות: מייצגת את רכיב השרת ``ClickOutsideBoardError`` ומרכזת את התנהגותו."""
    def __init__(self):
        """Initialize the instance and its dependencies.

        מאתחלת את המופע ואת התלויות שלו."""
        super().__init__(ERR_CLICK_OUTSIDE_BOARD)


class ClickEmptySourceError(UserInputError):
    """Represent the server-side click empty source error concept.

    מייצגת את רכיב השרת ``ClickEmptySourceError`` ומרכזת את התנהגותו.

    Responsibility: Represent the server-side click empty source error concept.

    אחריות: מייצגת את רכיב השרת ``ClickEmptySourceError`` ומרכזת את התנהגותו."""
    def __init__(self):
        """Initialize the instance and its dependencies.

        מאתחלת את המופע ואת התלויות שלו."""
        super().__init__(ERR_CLICK_EMPTY_SOURCE)


class JumpOutsideBoardError(UserInputError):
    """Represent the server-side jump outside board error concept.

    מייצגת את רכיב השרת ``JumpOutsideBoardError`` ומרכזת את התנהגותו.

    Responsibility: Represent the server-side jump outside board error concept.

    אחריות: מייצגת את רכיב השרת ``JumpOutsideBoardError`` ומרכזת את התנהגותו."""
    def __init__(self):
        """Initialize the instance and its dependencies.

        מאתחלת את המופע ואת התלויות שלו."""
        super().__init__(ERR_JUMP_OUTSIDE_BOARD)


class JumpEmptySourceError(UserInputError):
    """Represent the server-side jump empty source error concept.

    מייצגת את רכיב השרת ``JumpEmptySourceError`` ומרכזת את התנהגותו.

    Responsibility: Represent the server-side jump empty source error concept.

    אחריות: מייצגת את רכיב השרת ``JumpEmptySourceError`` ומרכזת את התנהגותו."""
    def __init__(self):
        """Initialize the instance and its dependencies.

        מאתחלת את המופע ואת התלויות שלו."""
        super().__init__(ERR_JUMP_EMPTY_SOURCE)


class GameOverError(UserInputError):
    """Represent the server-side game over error concept.

    מייצגת את רכיב השרת ``GameOverError`` ומרכזת את התנהגותו.

    Responsibility: Represent the server-side game over error concept.

    אחריות: מייצגת את רכיב השרת ``GameOverError`` ומרכזת את התנהגותו."""
    def __init__(self):
        """Initialize the instance and its dependencies.

        מאתחלת את המופע ואת התלויות שלו."""
        super().__init__(ERR_GAME_OVER)


class MotionInProgressError(UserInputError):
    """Represent the server-side motion in progress error concept.

    מייצגת את רכיב השרת ``MotionInProgressError`` ומרכזת את התנהגותו.

    Responsibility: Represent the server-side motion in progress error concept.

    אחריות: מייצגת את רכיב השרת ``MotionInProgressError`` ומרכזת את התנהגותו."""
    def __init__(self):
        """Initialize the instance and its dependencies.

        מאתחלת את המופע ואת התלויות שלו."""
        super().__init__(ERR_MOTION_IN_PROGRESS)


class EmptySourceError(UserInputError):
    """Represent the server-side empty source error concept.

    מייצגת את רכיב השרת ``EmptySourceError`` ומרכזת את התנהגותו.

    Responsibility: Represent the server-side empty source error concept.

    אחריות: מייצגת את רכיב השרת ``EmptySourceError`` ומרכזת את התנהגותו."""
    def __init__(self):
        """Initialize the instance and its dependencies.

        מאתחלת את המופע ואת התלויות שלו."""
        super().__init__(ERR_EMPTY_SOURCE)


class FriendlyDestinationError(UserInputError):
    """Represent the server-side friendly destination error concept.

    מייצגת את רכיב השרת ``FriendlyDestinationError`` ומרכזת את התנהגותו.

    Responsibility: Represent the server-side friendly destination error concept.

    אחריות: מייצגת את רכיב השרת ``FriendlyDestinationError`` ומרכזת את התנהגותו."""
    def __init__(self):
        """Initialize the instance and its dependencies.

        מאתחלת את המופע ואת התלויות שלו."""
        super().__init__(ERR_FRIENDLY_DESTINATION)


class IllegalPieceMoveError(UserInputError):
    """Represent the server-side illegal piece move error concept.

    מייצגת את רכיב השרת ``IllegalPieceMoveError`` ומרכזת את התנהגותו.

    Responsibility: Represent the server-side illegal piece move error concept.

    אחריות: מייצגת את רכיב השרת ``IllegalPieceMoveError`` ומרכזת את התנהגותו."""
    def __init__(self):
        """Initialize the instance and its dependencies.

        מאתחלת את המופע ואת התלויות שלו."""
        super().__init__(ERR_ILLEGAL_PIECE_MOVE)


def raise_for_move_reason(reason: MoveReason) -> None:
    """Converts a rejected move reason into a user-facing exception.

    מבצעת את פעולת ``raise`` ``for`` המהלך הסיבה."""

    reason_to_error = {
        MoveReason.GAME_OVER: GameOverError,
        MoveReason.MOTION_IN_PROGRESS: MotionInProgressError,
        MoveReason.OUTSIDE_BOARD: ClickOutsideBoardError,
        MoveReason.EMPTY_SOURCE: EmptySourceError,
        MoveReason.FRIENDLY_DESTINATION: FriendlyDestinationError,
        MoveReason.ILLEGAL_PIECE_MOVE: IllegalPieceMoveError,
    }

    error_type = reason_to_error.get(reason)

    if error_type is None:
        raise UserInputError(str(reason.value))

    raise error_type()
