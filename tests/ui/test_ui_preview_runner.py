"""Tests for headless UI preview script behavior."""

from pathlib import Path
import unittest

from tools.ui import preview_runner


class TestUIPreviewRunner(unittest.TestCase):
    def test_main_saves_preview_without_opening_window(self):
        output_path = Path("view/ui/assets/preview/test_preview_output.jpg")

        if output_path.exists():
            output_path.unlink()

        generated = preview_runner.main(
            show_window=False,
            output_path=output_path,
        )

        self.assertEqual(generated, output_path)
        self.assertTrue(output_path.exists())
        self.assertGreater(output_path.stat().st_size, 0)
