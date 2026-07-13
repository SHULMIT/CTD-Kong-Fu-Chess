"""System tests for main entrypoint script execution."""

import io
import unittest
from unittest.mock import patch

import main


class TestMainEntrypoint(unittest.TestCase):
    def test_main_runs_click_wait_print_flow(self):
        stdin_data = "\n".join([
            "Board:",
            "wR .",
            "Commands:",
            "click 0 0",
            "click 100 0",
            "wait 1000",
            "print board",
        ])

        with patch("sys.stdin", io.StringIO(stdin_data)), patch(
            "sys.stdout", new_callable=io.StringIO
        ) as stdout:
            main.main()

        output = stdout.getvalue().strip()

        self.assertEqual(output, ". wR")

    def test_main_prints_parser_error_for_invalid_board(self):
        stdin_data = "\n".join([
            "Board:",
            "xX .",
            "Commands:",
            "print board",
        ])

        with patch("sys.stdin", io.StringIO(stdin_data)), patch(
            "sys.stdout", new_callable=io.StringIO
        ) as stdout:
            main.main()

        output = stdout.getvalue().strip()

        self.assertEqual(output, "ERROR UNKNOWN_TOKEN")
