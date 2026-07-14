from view.ui.animation.animation_state import AnimationState
from view.ui.animation.sprite_animation import SpriteAnimation
from view.ui.constants.ui_paths import PIECES_ASSETS_DIR
from view.ui.graphics.img import Img


class SpriteLoader:
    """Loads the numbered PNG frames for one piece animation."""

    @staticmethod
    def load(
        piece_code: str,
        state: AnimationState,
        size: tuple[int, int],
    ) -> SpriteAnimation:
        sprites_dir = PIECES_ASSETS_DIR / piece_code / "states" / state.value / "sprites"
        frame_paths = sorted(sprites_dir.glob("*.png"), key=lambda path: int(path.stem))

        if not frame_paths:
            raise FileNotFoundError(
                f"No sprites found for {piece_code!r} in state {state.value!r}."
            )

        return SpriteAnimation([Img().read(path, size=size) for path in frame_paths])
