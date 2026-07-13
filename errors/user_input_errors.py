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
from game.move_result import MoveReason as GameMoveReason
from rules.move_reason import MoveReason as RuleMoveReason


class UserInputError(Exception):
    """
    Base error for invalid user input that should be shown to the user.
    """


class EmptyCommandError(UserInputError):
    def __init__(self):
        super().__init__(ERR_EMPTY_COMMAND)


class UnknownCommandError(UserInputError):
    def __init__(self):
        super().__init__(ERR_UNKNOWN_COMMAND)


class ClickOutsideBoardError(UserInputError):
    def __init__(self):
        super().__init__(ERR_CLICK_OUTSIDE_BOARD)


class ClickEmptySourceError(UserInputError):
    def __init__(self):
        super().__init__(ERR_CLICK_EMPTY_SOURCE)


class JumpOutsideBoardError(UserInputError):
    def __init__(self):
        super().__init__(ERR_JUMP_OUTSIDE_BOARD)


class JumpEmptySourceError(UserInputError):
    def __init__(self):
        super().__init__(ERR_JUMP_EMPTY_SOURCE)


class GameOverError(UserInputError):
    def __init__(self):
        super().__init__(ERR_GAME_OVER)


class MotionInProgressError(UserInputError):
    def __init__(self):
        super().__init__(ERR_MOTION_IN_PROGRESS)


class EmptySourceError(UserInputError):
    def __init__(self):
        super().__init__(ERR_EMPTY_SOURCE)


class FriendlyDestinationError(UserInputError):
    def __init__(self):
        super().__init__(ERR_FRIENDLY_DESTINATION)


class IllegalPieceMoveError(UserInputError):
    def __init__(self):
        super().__init__(ERR_ILLEGAL_PIECE_MOVE)


def raise_for_move_reason(reason: GameMoveReason | RuleMoveReason) -> None:
    """
    Converts a rejected move reason into a user-facing exception.
    """

    reason_to_error = {
        GameMoveReason.GAME_OVER: GameOverError,
        GameMoveReason.MOTION_IN_PROGRESS: MotionInProgressError,
        GameMoveReason.EMPTY_SOURCE: EmptySourceError,
        GameMoveReason.FRIENDLY_DESTINATION: FriendlyDestinationError,
        GameMoveReason.ILLEGAL_PIECE_MOVE: IllegalPieceMoveError,
        RuleMoveReason.OUTSIDE_BOARD: ClickOutsideBoardError,
        RuleMoveReason.EMPTY_SOURCE: EmptySourceError,
        RuleMoveReason.FRIENDLY_DESTINATION: FriendlyDestinationError,
        RuleMoveReason.ILLEGAL_PIECE_MOVE: IllegalPieceMoveError,
    }

    error_type = reason_to_error.get(reason)

    if error_type is None:
        raise UserInputError(str(reason.value))

    raise error_type()