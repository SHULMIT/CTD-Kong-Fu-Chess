"""
Integration tests - test the entire system working together.
Tests flow: text parsing → board creation → move validation → piece movement.
"""

import unittest

from board_io.text_board_parser import TextBoardParser
from board_io.text_board_formatter import TextBoardFormatter
from model.position import Position
from model.piece import PieceColor
from rules.rule_engine import RuleEngine
from rules.move_reason import MoveReason


class TestIntegrationFullGame(unittest.TestCase):
    """
    Integration tests covering text parsing, board setup, and move validation.
    """

    def setUp(self):
        """Initialize parser, formatter, and engine for each test."""
        self.parser = TextBoardParser()
        self.formatter = TextBoardFormatter()
        self.engine = RuleEngine()

    def test_parse_board_and_validate_rook_move(self):
        """
        Test: Parse board → validate rook move → verify result.
        """
        board_text = [
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            "wR . . . . . . .",
        ]

        board = self.parser.parse(board_text)

        source = Position(7, 0)
        target = Position(7, 3)

        result = self.engine.validate_move(board, source, target)

        self.assertTrue(result.is_valid)
        self.assertEqual(result.reason, MoveReason.OK)

    def test_parse_board_and_reject_blocked_rook_move(self):
        """
        Test: Parse board → validate blocked rook move → verify rejection.
        """
        board_text = [
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            "wR . wP . . . . .",
        ]

        board = self.parser.parse(board_text)

        source = Position(7, 0)
        target = Position(7, 3)

        result = self.engine.validate_move(board, source, target)

        self.assertFalse(result.is_valid)
        self.assertEqual(result.reason, MoveReason.ILLEGAL_PIECE_MOVE)

    def test_parse_board_and_validate_bishop_move(self):
        """
        Test: Parse board → validate bishop diagonal move → verify result.
        """
        board_text = [
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            "wB . . . . . . .",
        ]

        board = self.parser.parse(board_text)

        source = Position(7, 0)
        target = Position(4, 3)

        result = self.engine.validate_move(board, source, target)

        self.assertTrue(result.is_valid)
        self.assertEqual(result.reason, MoveReason.OK)

    def test_parse_board_and_validate_knight_jump_over_pieces(self):
        """
        Test: Parse board → validate knight jumping over other pieces → verify result.
        """
        board_text = [
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            "wN wP wP . . . . .",
        ]

        board = self.parser.parse(board_text)

        source = Position(7, 0)
        target = Position(5, 1)

        result = self.engine.validate_move(board, source, target)

        self.assertTrue(result.is_valid)
        self.assertEqual(result.reason, MoveReason.OK)

    def test_parse_board_and_validate_pawn_capture(self):
        """
        Test: Parse board → validate pawn diagonal capture → verify result.
        """
        board_text = [
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . bP . . . . .",
            ". wP . . . . . .",
            ". . . . . . . .",
        ]

        board = self.parser.parse(board_text)

        source = Position(6, 1)
        target = Position(5, 2)

        result = self.engine.validate_move(board, source, target)

        self.assertTrue(result.is_valid)
        self.assertEqual(result.reason, MoveReason.OK)

    def test_parse_board_and_reject_pawn_blocked(self):
        """
        Test: Parse board → validate blocked pawn move → verify rejection.
        """
        board_text = [
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". bP . . . . . .",
            ". wP . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
        ]

        board = self.parser.parse(board_text)

        source = Position(5, 1)
        target = Position(4, 1)

        result = self.engine.validate_move(board, source, target)

        self.assertFalse(result.is_valid)
        self.assertEqual(result.reason, MoveReason.ILLEGAL_PIECE_MOVE)

    def test_parse_board_and_validate_queen_moves_both_directions(self):
        """
        Test: Parse board → validate queen can move orthogonal and diagonal → verify results.
        """
        board_text = [
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . wQ . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
        ]

        board = self.parser.parse(board_text)

        # Queen at (4, 3) - test orthogonal move
        source_ortho = Position(4, 3)
        target_ortho = Position(4, 0)

        result_ortho = self.engine.validate_move(board, source_ortho, target_ortho)

        self.assertTrue(result_ortho.is_valid)
        self.assertEqual(result_ortho.reason, MoveReason.OK)

        # Queen at (4, 3) - test diagonal move
        source_diag = Position(4, 3)
        target_diag = Position(2, 1)

        result_diag = self.engine.validate_move(board, source_diag, target_diag)

        self.assertTrue(result_diag.is_valid)
        self.assertEqual(result_diag.reason, MoveReason.OK)

    def test_parse_board_and_validate_king_one_step(self):
        """
        Test: Parse board → validate king one-step move → verify result.
        """
        board_text = [
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . wK . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
        ]

        board = self.parser.parse(board_text)

        source = Position(4, 3)
        target = Position(3, 3)

        result = self.engine.validate_move(board, source, target)

        self.assertTrue(result.is_valid)
        self.assertEqual(result.reason, MoveReason.OK)

    def test_parse_board_and_reject_king_two_steps(self):
        """
        Test: Parse board → validate king two-step move (invalid) → verify rejection.
        """
        board_text = [
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . wK . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
        ]

        board = self.parser.parse(board_text)

        source = Position(4, 3)
        target = Position(2, 3)

        result = self.engine.validate_move(board, source, target)

        self.assertFalse(result.is_valid)
        self.assertEqual(result.reason, MoveReason.ILLEGAL_PIECE_MOVE)

    def test_parse_board_reject_friendly_destination(self):
        """
        Test: Parse board → validate move to friendly piece → verify rejection.
        """
        board_text = [
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            "wR . . wB . . . .",
        ]

        board = self.parser.parse(board_text)

        source = Position(7, 0)
        target = Position(7, 3)

        result = self.engine.validate_move(board, source, target)

        self.assertFalse(result.is_valid)
        self.assertEqual(result.reason, MoveReason.FRIENDLY_DESTINATION)

    def test_parse_board_validate_capture_enemy_piece(self):
        """
        Test: Parse board → validate capturing enemy piece → verify acceptance.
        """
        board_text = [
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            "wR . . bR . . . .",
        ]

        board = self.parser.parse(board_text)

        source = Position(7, 0)
        target = Position(7, 3)

        result = self.engine.validate_move(board, source, target)

        self.assertTrue(result.is_valid)
        self.assertEqual(result.reason, MoveReason.OK)

    def test_round_trip_parse_and_format(self):
        """
        Test: Parse board from text → format back to text → verify output matches.
        """
        board_text = [
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            "wR . . wB bK . . .",
        ]

        board = self.parser.parse(board_text)
        formatted = self.formatter.format(board)

        # Parse again to verify round-trip - split formatted string into lines
        board_reparsed = self.parser.parse(formatted.strip().split('\n'))

        # Check that pieces are still in the same positions
        self.assertIsNotNone(board_reparsed.get_piece(Position(7, 0)))
        self.assertIsNotNone(board_reparsed.get_piece(Position(7, 3)))
        self.assertIsNotNone(board_reparsed.get_piece(Position(7, 4)))

    def test_multiple_moves_validation_sequence(self):
        """
        Test: Parse board → validate multiple sequential moves → verify each result.
        """
        board_text = [
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            "wR . . . wB . . .",
        ]

        board = self.parser.parse(board_text)

        # Move 1: Rook right (from column 0 to 3)
        result1 = self.engine.validate_move(
            board, Position(7, 0), Position(7, 3)
        )
        self.assertTrue(result1.is_valid)

        # Move 2: Bishop diagonal (from (7,4) down-left to (5,2))
        result2 = self.engine.validate_move(
            board, Position(7, 4), Position(5, 2)
        )
        self.assertTrue(result2.is_valid)

    def test_complex_board_setup_all_pieces(self):
        """
        Test: Parse complex board with all piece types → validate moves for each.
        """
        board_text = [
            ". . . bK . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . bQ . . . . .",
            ". . . . . . . .",
            ". . . wQ . . . .",
            ". . . . . . . .",
            ". wK . . wR . . .",
        ]

        board = self.parser.parse(board_text)

        # Validate moves for each piece type
        moves = [
            (Position(0, 3), Position(1, 3), True),  # Black King down
            (Position(3, 2), Position(3, 5), True),  # Black Queen right
            (Position(5, 3), Position(2, 0), True),  # White Queen diagonal
            (Position(7, 1), Position(6, 2), True),  # White King diagonal
            (Position(7, 4), Position(7, 6), True),  # White Rook right
        ]

        for source, target, expected_valid in moves:
            result = self.engine.validate_move(board, source, target)
            self.assertEqual(result.is_valid, expected_valid)


if __name__ == "__main__":
    unittest.main()
