from enum import Enum


class AnimationState(Enum):
    IDLE = "idle"
    MOVE = "move"
    JUMP = "jump"
    SHORT_REST = "short_rest"
    LONG_REST = "long_rest"
    DEAD = "dead"