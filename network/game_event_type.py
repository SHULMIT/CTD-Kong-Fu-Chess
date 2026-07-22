"""Shared discriminators for game events carried by the network protocol."""

from enum import Enum


class GameEventType(str, Enum):
    """Stable wire names for events nested inside ``game_event`` messages."""

    MOVE_STARTED = "move_started"
    MOVE_COMPLETED = "move_completed"
    JUMP_STARTED = "jump_started"
    JUMP_COMPLETED = "jump_completed"
    SCORE_CHANGED = "score_changed"
    GAME_OVER = "game_over"
