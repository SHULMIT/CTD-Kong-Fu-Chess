from dataclasses import dataclass

from view.ui.graphics.img import Img


@dataclass
class SpriteAnimation:
    """
    Represents a single animation of a game piece.

    Example:
        idle
        move
        jump
    """

    name: str

    frames: list[Img]

    fps: int

    loop: bool

    next_state: str | None

    speed: float