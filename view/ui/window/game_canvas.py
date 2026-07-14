from view.ui.graphics.img import Img


class GameCanvas:
    """
    Represents the main canvas of the game.

    Every graphical element is drawn on this canvas.
    """

    def __init__(self, background_source: str | Img):
        """
        Creates the main canvas from the background image.

        :param background_source: Path to the background image
            or a preloaded Img instance.
        """
        if isinstance(background_source, Img):
            self._canvas = background_source
        else:
            self._canvas = Img().read(background_source)

    @property
    def canvas(self) -> Img:
        """
        Returns the current canvas.
        """
        return self._canvas

    def show(self) -> None:
        """
        Displays the current canvas.
        """
        self._canvas.show()