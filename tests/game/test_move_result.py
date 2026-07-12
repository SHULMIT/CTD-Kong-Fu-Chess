"""
Tests for game.move_result.
"""

from dataclasses import FrozenInstanceError
import unittest

from game.move_result import MoveReason, MoveResult


class TestMoveResult(unittest.TestCase):
    def test_accepted_returns_ok(self):
        result = MoveResult.accepted()

        self.assertTrue(result.is_accepted)
        self.assertEqual(result.reason, MoveReason.OK)

    def test_rejected_returns_given_reason(self):
        result = MoveResult.rejected(MoveReason.OUTSIDE_BOARD)

        self.assertFalse(result.is_accepted)
        self.assertEqual(result.reason, MoveReason.OUTSIDE_BOARD)

    def test_move_result_is_frozen(self):
        result = MoveResult.accepted()

        with self.assertRaises(FrozenInstanceError):
            result.reason = MoveReason.GAME_OVER
