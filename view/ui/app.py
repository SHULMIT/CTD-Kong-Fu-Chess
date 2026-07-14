from view.ui.window.game_canvas import GameCanvas
from view.ui.render.board_renderer import BoardRenderer
from view.ui.layout.board_layout import BoardLayout
from view.ui.constants.ui_paths import BACKGROUND_PATH, BOARD_PATH
from view.ui.constants.image_keys import ImageKeys
from view.ui.graphics.image_manager import ImageManager

def app():
    image_manager = ImageManager()
    image_manager.load(ImageKeys.BACKGROUND, BACKGROUND_PATH)

    canvas = GameCanvas(image_manager.get(ImageKeys.BACKGROUND))

    height, width = canvas.canvas.img.shape[:2]

    layout = BoardLayout(
        window_width=width,
        window_height=height
    )
    image_manager.load(
        ImageKeys.BOARD,
        BOARD_PATH,
        size=(layout.board_size, layout.board_size),
    )

    board_renderer = BoardRenderer(
        canvas=canvas,
        board_source=image_manager.get(ImageKeys.BOARD),
        x=layout.board_x,
        y=layout.board_y,
    )

    board_renderer.draw()

    canvas.show()


if __name__ == "__main__":
    app()
