from pathlib import Path

UI_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = UI_DIR / "assets"
BOARD_ASSETS_DIR = ASSETS_DIR / "board"
PREVIEW_ASSETS_DIR = ASSETS_DIR / "preview"
# ``pieces2`` contains the clean transparent Kung Fu sprites.  The older
# ``pieces1`` set includes debug labels baked into the PNG files.
PIECES_ASSETS_DIR = ASSETS_DIR / "pieces2"

BACKGROUND_PATH = BOARD_ASSETS_DIR / "background.jpg"
BOARD_PATH = BOARD_ASSETS_DIR / "Board.jpg"
DEFAULT_PREVIEW_OUTPUT_PATH = PREVIEW_ASSETS_DIR / "preview_output.jpg"
DEFAULT_GAME_DEMO_OUTPUT_DIR = PREVIEW_ASSETS_DIR / "game_demo"
