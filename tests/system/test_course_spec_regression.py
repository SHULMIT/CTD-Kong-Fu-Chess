"""Regression tests matching external course-style stdin/stdout scenarios."""

import io
import unittest
from unittest.mock import patch

import main


class TestCourseSpecRegression(unittest.TestCase):
    def _run_main(self, stdin_data: str) -> str:
        with patch("sys.stdin", io.StringIO(stdin_data)), patch(
            "sys.stdout", new_callable=io.StringIO
        ) as stdout:
            main.main()
        return stdout.getvalue().strip()

    def test_parse_rectangular_board_3x4(self):
        stdin_data = "\n".join(
            [
                "Board:",
                "wK . . bK",
                ". . . .",
                "wR . . bR",
                "Commands:",
                "print board",
            ]
        )

        output = self._run_main(stdin_data)

        self.assertEqual(output, "wK . . bK\n. . . .\nwR . . bR")

    def test_parse_piece_tokens_and_colors(self):
        stdin_data = "\n".join(
            [
                "Board:",
                "wK . bQ",
                ". wN .",
                "bP . wR",
                "Commands:",
                "print board",
            ]
        )

        output = self._run_main(stdin_data)

        self.assertEqual(output, "wK . bQ\n. wN .\nbP . wR")

    def test_reject_unknown_token(self):
        stdin_data = "\n".join(
            [
                "Board:",
                "wK xZ",
                ". .",
                "Commands:",
            ]
        )

        output = self._run_main(stdin_data)

        self.assertEqual(output, "ERROR UNKNOWN_TOKEN")

    def test_reject_row_width_mismatch(self):
        stdin_data = "\n".join(
            [
                "Board:",
                "wK . .",
                ". bK",
                "Commands:",
            ]
        )

        output = self._run_main(stdin_data)

        self.assertEqual(output, "ERROR ROW_WIDTH_MISMATCH")

    def test_select_piece_by_center_click(self):
        stdin_data = "\n".join(
            [
                "Board:",
                "wK . .",
                ". . .",
                ". . .",
                "Commands:",
                "click 50 50",
                "click 150 150",
                "wait 1000",
                "print board",
            ]
        )

        output = self._run_main(stdin_data)

        self.assertEqual(output, ". . .\n. wK .\n. . .")

    def test_click_empty_cell_does_not_select(self):
        stdin_data = "\n".join(
            [
                "Board:",
                "wK . .",
                ". . .",
                ". . .",
                "Commands:",
                "click 150 150",
                "click 250 250",
                "wait 1000",
                "print board",
            ]
        )

        output = self._run_main(stdin_data)

        self.assertEqual(output, "wK . .\n. . .\n. . .")

    def test_click_outside_board_is_ignored(self):
        stdin_data = "\n".join(
            [
                "Board:",
                "wK . .",
                ". . .",
                ". . .",
                "Commands:",
                "click 350 50",
                "click -10 50",
                "print board",
            ]
        )

        output = self._run_main(stdin_data)

        self.assertEqual(output, "wK . .\n. . .\n. . .")

    def test_clicking_another_piece_replaces_selection(self):
        stdin_data = "\n".join(
            [
                "Board:",
                "wR . wK",
                ". . .",
                "Commands:",
                "click 50 50",
                "click 250 50",
                "click 250 150",
                "wait 1000",
                "print board",
            ]
        )

        output = self._run_main(stdin_data)

        self.assertEqual(output, "wR . .\n. . wK")

    def test_reject_unknown_token_with_print_board(self):
        stdin_data = "\n".join(
            [
                "Board:",
                "wK xZ",
                ". .",
                "Commands:",
                "print board",
            ]
        )

        output = self._run_main(stdin_data)

        self.assertEqual(output, "ERROR UNKNOWN_TOKEN")

    def test_reject_row_width_mismatch_with_print_board(self):
        stdin_data = "\n".join(
            [
                "Board:",
                "wK . .",
                ". bK",
                "Commands:",
                "print board",
            ]
        )

        output = self._run_main(stdin_data)

        self.assertEqual(output, "ERROR ROW_WIDTH_MISMATCH")

    def test_king_one_step_valid(self):
        stdin_data = "\n".join(
            [
                "Board:",
                "wK . .",
                ". . .",
                ". . .",
                "Commands:",
                "click 50 50",
                "click 150 150",
                "wait 1000",
                "print board",
            ]
        )

        output = self._run_main(stdin_data)

        self.assertEqual(output, ". . .\n. wK .\n. . .")

    def test_king_two_steps_invalid(self):
        stdin_data = "\n".join(
            [
                "Board:",
                "wK . .",
                ". . .",
                ". . .",
                "Commands:",
                "click 50 50",
                "click 250 250",
                "wait 1000",
                "print board",
            ]
        )

        output = self._run_main(stdin_data)

        self.assertEqual(output, "wK . .\n. . .\n. . .")

    def test_rook_straight_valid(self):
        stdin_data = "\n".join(
            [
                "Board:",
                "wR . .",
                "Commands:",
                "click 50 50",
                "click 250 50",
                "wait 2000",
                "print board",
            ]
        )

        output = self._run_main(stdin_data)

        self.assertEqual(output, ". . wR")

    def test_rook_diagonal_invalid(self):
        stdin_data = "\n".join(
            [
                "Board:",
                "wR . .",
                ". . .",
                ". . .",
                "Commands:",
                "click 50 50",
                "click 150 150",
                "wait 1000",
                "print board",
            ]
        )

        output = self._run_main(stdin_data)

        self.assertEqual(output, "wR . .\n. . .\n. . .")

    def test_bishop_diagonal_valid(self):
        stdin_data = "\n".join(
            [
                "Board:",
                "wB . .",
                ". . .",
                ". . .",
                "Commands:",
                "click 50 50",
                "click 250 250",
                "wait 2000",
                "print board",
            ]
        )

        output = self._run_main(stdin_data)

        self.assertEqual(output, ". . .\n. . .\n. . wB")

    def test_knight_l_valid(self):
        stdin_data = "\n".join(
            [
                "Board:",
                "wN . .",
                ". . .",
                ". . .",
                "Commands:",
                "click 50 50",
                "click 150 250",
                "wait 3000",
                "print board",
            ]
        )

        output = self._run_main(stdin_data)

        self.assertEqual(output, ". . .\n. . .\n. wN .")

    def test_queen_diagonal_valid(self):
        stdin_data = "\n".join(
            [
                "Board:",
                "wQ . .",
                ". . .",
                ". . .",
                "Commands:",
                "click 50 50",
                "click 250 250",
                "wait 2000",
                "print board",
            ]
        )

        output = self._run_main(stdin_data)

        self.assertEqual(output, ". . .\n. . .\n. . wQ")

    def test_rook_blocked_by_own_piece(self):
        stdin_data = "\n".join(
            [
                "Board:",
                "wR wP .",
                "Commands:",
                "click 50 50",
                "click 250 50",
                "wait 2000",
                "print board",
            ]
        )

        output = self._run_main(stdin_data)

        self.assertEqual(output, "wR wP .")

    def test_bishop_blocked_by_own_piece(self):
        stdin_data = "\n".join(
            [
                "Board:",
                "wB . .",
                ". wP .",
                ". . .",
                "Commands:",
                "click 50 50",
                "click 250 250",
                "wait 2000",
                "print board",
            ]
        )

        output = self._run_main(stdin_data)

        self.assertEqual(output, "wB . .\n. wP .\n. . .")

    def test_knight_jumps_over_blockers(self):
        stdin_data = "\n".join(
            [
                "Board:",
                "wN wP .",
                "wP . .",
                ". . .",
                "Commands:",
                "click 50 50",
                "click 150 250",
                "wait 3000",
                "print board",
            ]
        )

        output = self._run_main(stdin_data)

        self.assertEqual(output, ". wP .\nwP . .\n. wN .")

    def test_airborne_piece_captures_arriving_enemy(self):
        stdin_data = "\n".join(
            [
                "Board:",
                ". . .",
                "wK bR .",
                ". . .",
                "Commands:",
                "jump 50 150",
                "click 150 150",
                "click 50 150",
                "wait 1000",
                "print board",
            ]
        )

        output = self._run_main(stdin_data)

        self.assertEqual(output, ". . .\nwK . .\n. . .")

    def test_enemy_arrives_after_landing_captures_normally(self):
        stdin_data = "\n".join(
            [
                "Board:",
                ". . . .",
                "wK . . bR",
                ". . . .",
                "Commands:",
                "jump 50 150",
                "wait 1000",
                "click 350 150",
                "click 50 150",
                "wait 3000",
                "print board",
            ]
        )

        output = self._run_main(stdin_data)

        self.assertEqual(output, ". . . .\nbR . . .\n. . . .")
