from view.ui.animation.animation_state import AnimationState
from view.ui.animation.sprite_animation import SpriteAnimation
from view.ui.animation.sprite_loader import SpriteLoader


class AnimationRepository:
    """Caches resized animations so drawing a board does not reload files."""

    def __init__(self):
        self._animations: dict[tuple[str, AnimationState, tuple[int, int]], SpriteAnimation] = {}

    def get(
        self,
        piece_code: str,
        state: AnimationState,
        size: tuple[int, int],
    ) -> SpriteAnimation:
        key = (piece_code, state, size)
        if key not in self._animations:
            self._animations[key] = SpriteLoader.load(piece_code, state, size)
        return self._animations[key]
