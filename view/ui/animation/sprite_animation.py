from view.ui.graphics.img import Img


class SpriteAnimation:
    """A loaded, ordered sequence of sprite frames."""

    def __init__(self, frames: list[Img]):
        if not frames:
            raise ValueError("An animation needs at least one frame.")
        self._frames = tuple(frames)

    @property
    def frames(self) -> tuple[Img, ...]:
        return self._frames
