"""
Tests for game.request_move_service.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock
import unittest

from game.request_move_service import RequestMoveService
from game.move_reason import MoveReason


class TestRequestMoveService(unittest.TestCase):
    def test_request_move_rejected_when_validation_fails(self):
        board = MagicMock()
        rule_engine = MagicMock()
        arbiter = MagicMock()
        duration_calculator = MagicMock()

        rule_engine.validate_move.return_value = SimpleNamespace(
            is_valid=False,
            reason=MoveReason.ILLEGAL_PIECE_MOVE,
        )

        service = RequestMoveService(
            board=board,
            rule_engine=rule_engine,
            arbiter=arbiter,
            duration_calculator=duration_calculator,
        )

        source = MagicMock()
        target = MagicMock()
        result = service.request_move(source, target)

        self.assertFalse(result.is_accepted)
        self.assertEqual(result.reason, MoveReason.ILLEGAL_PIECE_MOVE)
        arbiter.start_motion.assert_not_called()
        duration_calculator.calculate.assert_not_called()

    def test_request_move_accepts_and_schedules_motion(self):
        board = MagicMock()
        rule_engine = MagicMock()
        arbiter = MagicMock()
        duration_calculator = MagicMock()

        rule_engine.validate_move.return_value = SimpleNamespace(
            is_valid=True,
            reason=MoveReason.OK,
        )

        duration_calculator.calculate.return_value = 3000

        piece = MagicMock()
        board.get_piece.return_value = piece

        service = RequestMoveService(
            board=board,
            rule_engine=rule_engine,
            arbiter=arbiter,
            duration_calculator=duration_calculator,
        )

        source = MagicMock()
        target = MagicMock()
        result = service.request_move(source, target)

        self.assertTrue(result.is_accepted)
        self.assertEqual(result.reason, MoveReason.OK)
        duration_calculator.calculate.assert_called_once_with(piece, source, target)
        arbiter.start_motion.assert_called_once_with(
            piece=piece,
            source=source,
            target=target,
            duration=3000,
        )
