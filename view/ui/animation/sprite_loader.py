import json
from pathlib import Path

from view.ui.animation.animation_state import AnimationState
from view.ui.animation.sprite_animation import SpriteAnimation
from view.ui.graphics.img import Img
from view.ui.constants.ui_paths import CURRENT_PIECES_PATH


class SpriteLoader:
    """
    sprite_loader.py

    Loads sprite animations from the assets folder.

    Responsibilities:
        - Load animation files.
        - Create SpriteAnimation objects.
    """

    def load(
        self,
        piece_code: str,
        state: AnimationState,
        size: tuple[int, int]
    ) -> SpriteAnimation:

        animation_folder = (
            CURRENT_PIECES_PATH /
            piece_code /
            "states" /
            state.value
        )

        config_path = animation_folder / "config.json"

        sprites_folder = animation_folder / "sprites"

        with open(config_path, encoding="utf-8") as file:
            config = json.load(file)

        frames = []

        image_files = sorted(
            sprites_folder.glob("*.png"),
            key=lambda path: int(path.stem)
        )

        for image_path in image_files:

            frame = Img().read(
                image_path,
                size=size,
                keep_aspect=True
            )

            frames.append(frame)

        return SpriteAnimation(
            name=state.value,
            frames=frames,
            fps=config["graphics"]["frames_per_sec"],
            loop=config["graphics"]["is_loop"],
            next_state=config["physics"]["next_state_when_finished"],
            speed=config["physics"]["speed_m_per_sec"]
        )
