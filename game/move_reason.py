"""Defines the canonical reasons produced by move processing and validation."""

from enum import Enum


class MoveReason(Enum):
    """Machine-readable outcomes for move validation and game requests."""

    OK = "ok"
    GAME_OVER = "game_over"
    MOTION_IN_PROGRESS = "motion_in_progress"
    OUTSIDE_BOARD = "outside_board"
    EMPTY_SOURCE = "empty_source"
    FRIENDLY_DESTINATION = "friendly_destination"
    ILLEGAL_PIECE_MOVE = "illegal_piece_move"
