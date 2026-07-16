from pathlib import Path

UI_DIR = Path(__file__).resolve().parent.parent

ASSETS_DIR = UI_DIR / "assets"

# Board
BOARD_ASSETS_DIR = ASSETS_DIR / "board"

BACKGROUND_PATH = BOARD_ASSETS_DIR / "background.jpg"
BOARD_PATH = BOARD_ASSETS_DIR / "Board.jpg"

# Preview
PREVIEW_ASSETS_DIR = ASSETS_DIR / "preview"
DEFAULT_PREVIEW_OUTPUT_PATH = PREVIEW_ASSETS_DIR / "preview_output.jpg"

# Pieces
PIECES_1_PATH = ASSETS_DIR / "pieces1"
PIECES_2_PATH = ASSETS_DIR / "pieces2"

# Current piece set
CURRENT_PIECES_PATH = PIECES_2_PATH
PIECES_ASSETS_DIR = CURRENT_PIECES_PATH

DEFAULT_BOARD_PATH = ASSETS_DIR / "default_board.txt"

# Game demo output
DEFAULT_GAME_DEMO_OUTPUT_DIR = PREVIEW_ASSETS_DIR / "game_demo"
