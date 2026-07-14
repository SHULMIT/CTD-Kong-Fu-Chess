"""Smoke tests for UI modules under view/ui."""

import importlib
import unittest


try:
    import cv2  # noqa: F401
    HAS_CV2 = True
except ModuleNotFoundError:
    HAS_CV2 = False


class TestUISmoke(unittest.TestCase):
    def test_board_layout_class_is_valid(self):
        module = importlib.import_module("view.ui.layout.board_layout")
        board_layout = module.BoardLayout(window_width=1200, window_height=900)

        self.assertGreater(board_layout.board_size, 0)
        self.assertGreater(board_layout.square_size, 0)
        self.assertGreaterEqual(board_layout.board_x, 0)
        self.assertGreaterEqual(board_layout.board_y, 0)

    @unittest.skipUnless(HAS_CV2, "OpenCV (cv2) is not installed")
    def test_game_canvas_module_imports(self):
        module = importlib.import_module("view.ui.window.game_canvas")
        self.assertTrue(hasattr(module, "GameCanvas"))

    @unittest.skipUnless(HAS_CV2, "OpenCV (cv2) is not installed")
    def test_board_renderer_module_imports(self):
        module = importlib.import_module("view.ui.render.board_renderer")
        self.assertTrue(hasattr(module, "BoardRenderer"))
