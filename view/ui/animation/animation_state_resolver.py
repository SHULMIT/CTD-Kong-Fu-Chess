"""
animation_state_resolver.py

Converts piece states to animation states.

Responsibilities:
    - Resolve the correct animation state.
"""

from model.piece import PieceState
from view.ui.animation.animation_state import AnimationState


class AnimationStateResolver:

    @staticmethod
    def resolve(state: PieceState) -> AnimationState:

        mapping = {
            PieceState.IDLE: AnimationState.IDLE,
            PieceState.MOVING: AnimationState.MOVE,
            PieceState.AIRBORNE: AnimationState.JUMP,
            PieceState.CAPTURED: AnimationState.DEAD,
        }

        return mapping[state]