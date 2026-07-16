from view.ui.animation.animation_state import AnimationState
from view.ui.animation.sprite_animation import SpriteAnimation
from view.ui.animation.sprite_loader import SpriteLoader


class AnimationRepository:
    """
    Stores loaded animations in memory.

    Each animation is loaded only once.
    """

    def __init__(self):

        self._loader = SpriteLoader()

        self._animations: dict[
            tuple[str, AnimationState, tuple[int, int]],
            SpriteAnimation
        ] = {}

    def get(
            self,
            piece_code: str,
            state: AnimationState,
            size: tuple[int, int]
    ) -> SpriteAnimation:
        """
        Returns the requested animation.

        If the animation was not loaded before,
        it is loaded from disk and stored in memory.
        """

        key = (
            piece_code,
            state,
            size
        )

        if key not in self._animations:

            self._animations[key] = self._loader.load(
                piece_code=piece_code,
                state=state,
                size=size
            )

        return self._animations[key]

    def clear(self) -> None:
        """
        Removes all cached animations.
        """

        self._animations.clear()