from pathlib import Path

from view.ui.graphics.img import Img


class ImageManager:
    """
    image_manager.py

    Provides centralized management for UI images.

    Responsibilities:
        - Load images.
        - Cache images.
        - Provide images.
    mage is loaded only once and then reused.
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
     

        if not key:
            raise ValueError("Image key cannot be empty.")

        if key in self._images:
            raise ValueError(
                f"Image '{key}' is already loaded."
            )

        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(
                f"Image file was not found: {path}"
            )

        self._images[key] = Img().read(
            path,
            size=size,
            keep_aspect=keep_aspect
        )

    def get(
        self,
        key: str
    ) -> Img:
      

        if key not in self._images:
            raise KeyError(
                f"Image '{key}' was not loaded."
            )

        return self._images[key]

    def contains(
        self,
        key: str
    ) -> bool:
        """
        Returns True if the image exists.
        """

        return key in self._images

    def remove(
        self,
        key: str
    ) -> None:
        """
        Removes a loaded image.

        Raises:
            KeyError:
                If the image does not exist.
        """

        if key not in self._images:
            raise KeyError(
                f"Image '{key}' does not exist."
            )

        del self._images[key]

    @property
    def count(self) -> int:
        """
        Returns the number of loaded images.
        """

        return len(self._images)

    @property
    def loaded_keys(self) -> tuple[str, ...]:
        """
        Returns all loaded image keys.
        """

        return tuple(self._images.keys())

    def clear(self) -> None:
        """
        Removes every loaded image.
        """

        self._images.clear()