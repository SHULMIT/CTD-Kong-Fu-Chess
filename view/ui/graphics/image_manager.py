from pathlib import Path

from view.ui.constants.image_keys import ImageKeys
from view.ui.graphics.img import Img


class ImageManager:
    """
    Loads and stores all game images.

    Every image is loaded only once.
    """

    def __init__(self):
        self._images: dict[str, Img] = {}

    def load(
        self,
        key: str,
        path: str | Path,
        size: tuple[int, int] | None = None,
        keep_aspect: bool = False,
    ) -> None:
        """
        Load an image and store it in memory.
        """

        self._images[key] = Img().read(
            path,
            size=size,
            keep_aspect=keep_aspect,
        )

    def get(self, key: str) -> Img:
        """
        Returns a loaded image.
        """

        return self._images[key]

    def contains(self, key: str) -> bool:
        """
        Returns True if the image exists.
        """

        return key in self._images

    def clear(self) -> None:
        """
        Removes all loaded images.
        """

        self._images.clear()