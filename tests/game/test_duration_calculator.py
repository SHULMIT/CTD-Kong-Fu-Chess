"""
Tests for realtime.duration_calculator.
"""

import unittest

from config.constants import MILLISECONDS_PER_CELL
from model.piece import Piece, PieceColor, PieceState, PieceType
from model.position import Position
from realtime.duration_calculator import DurationCalculator


class TestDurationCalculator(unittest.TestCase):
    def setUp(self):
        self.calculator = DurationCalculator()

    def _make_piece(self, piece_type: PieceType) -> Piece:
        return Piece(
            piece_id=1,
            piece_type=piece_type,
            color=PieceColor.WHITE,
            position=Position(0, 0),
            state=PieceState.IDLE,
        )

    def test_calculate_horizontal_distance(self):
        piece = self._make_piece(PieceType.ROOK)

        duration = self.calculator.calculate(
            piece=piece,
            source=Position(3, 1),
            target=Position(3, 4),
        )

        self.assertEqual(duration, 3 * MILLISECONDS_PER_CELL)

    def test_calculate_vertical_distance(self):
        piece = self._make_piece(PieceType.ROOK)

        duration = self.calculator.calculate(
            piece=piece,
            source=Position(1, 5),
            target=Position(4, 5),
        )

        self.assertEqual(duration, 3 * MILLISECONDS_PER_CELL)

    def test_calculate_diagonal_distance(self):
        piece = self._make_piece(PieceType.BISHOP)

        duration = self.calculator.calculate(
            piece=piece,
            source=Position(2, 2),
            target=Position(5, 5),
        )

        self.assertEqual(duration, 3 * MILLISECONDS_PER_CELL)

    def test_calculate_knight_is_always_one_cell_time(self):
        piece = self._make_piece(PieceType.KNIGHT)

        duration = self.calculator.calculate(
            piece=piece,
            source=Position(4, 4),
            target=Position(2, 5),
        )

        self.assertEqual(duration, MILLISECONDS_PER_CELL)
