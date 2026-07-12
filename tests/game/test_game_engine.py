"""
Tests for game.game_engine.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock
import unittest

from game.game_engine import GameEngine
from game.move_result import MoveReason


class TestGameEngine(unittest.TestCase):
    def test_board_property_returns_injected_board(self):
        board = MagicMock()
        rule_engine = MagicMock()
        arbiter = MagicMock()
        duration_calculator = MagicMock()
        engine = GameEngine(
            board=board,
            rule_engine=rule_engine,
            arbiter=arbiter,
            duration_calculator=duration_calculator,
        )

        self.assertIs(engine.board, board)

    def test_game_over_defaults_to_false(self):
        engine = GameEngine(
            board=MagicMock(),
            rule_engine=MagicMock(),
            arbiter=MagicMock(),
            duration_calculator=MagicMock(),
        )

        self.assertFalse(engine.game_over)

    def test_request_move_rejected_when_game_over(self):
        board = MagicMock()
        rule_engine = MagicMock()
        arbiter = MagicMock()
        duration_calculator = MagicMock()
        engine = GameEngine(
            board=board,
            rule_engine=rule_engine,
            arbiter=arbiter,
            duration_calculator=duration_calculator,
        )
        engine._game_over = True

        source = MagicMock()
        target = MagicMock()

        result = engine.request_move(source, target)

        self.assertFalse(result.is_accepted)
        self.assertEqual(result.reason, MoveReason.GAME_OVER)
        rule_engine.validate_move.assert_not_called()
        arbiter.start_motion.assert_not_called()
        duration_calculator.calculate.assert_not_called()

    def test_request_move_rejected_when_motion_is_in_progress(self):
        board = MagicMock()
        rule_engine = MagicMock()
        arbiter = MagicMock()
        duration_calculator = MagicMock()
        arbiter.has_active_motion.return_value = True
        engine = GameEngine(
            board=board,
            rule_engine=rule_engine,
            arbiter=arbiter,
            duration_calculator=duration_calculator,
        )

        source = MagicMock()
        target = MagicMock()

        result = engine.request_move(source, target)

        self.assertFalse(result.is_accepted)
        self.assertEqual(result.reason, MoveReason.MOTION_IN_PROGRESS)
        rule_engine.validate_move.assert_not_called()
        arbiter.start_motion.assert_not_called()
        duration_calculator.calculate.assert_not_called()

    def test_request_move_rejected_when_validation_fails(self):
        board = MagicMock()
        rule_engine = MagicMock()
        arbiter = MagicMock()
        duration_calculator = MagicMock()
        arbiter.has_active_motion.return_value = False
        rule_engine.validate_move.return_value = SimpleNamespace(
            is_valid=False,
            reason=MoveReason.ILLEGAL_PIECE_MOVE,
        )
        engine = GameEngine(
            board=board,
            rule_engine=rule_engine,
            arbiter=arbiter,
            duration_calculator=duration_calculator,
        )

        source = MagicMock()
        target = MagicMock()

        result = engine.request_move(source, target)

        self.assertFalse(result.is_accepted)
        self.assertEqual(result.reason, MoveReason.ILLEGAL_PIECE_MOVE)
        rule_engine.validate_move.assert_called_once_with(board, source, target)
        arbiter.start_motion.assert_not_called()
        duration_calculator.calculate.assert_not_called()

    def test_request_move_accepts_and_starts_motion_when_validation_passes(self):
        board = MagicMock()
        rule_engine = MagicMock()
        arbiter = MagicMock()
        duration_calculator = MagicMock()
        arbiter.has_active_motion.return_value = False
        rule_engine.validate_move.return_value = SimpleNamespace(
            is_valid=True,
            reason=MoveReason.OK,
        )
        duration_calculator.calculate.return_value = 2000
        engine = GameEngine(
            board=board,
            rule_engine=rule_engine,
            arbiter=arbiter,
            duration_calculator=duration_calculator,
        )

        source = MagicMock()
        target = MagicMock()
        piece = MagicMock()
        board.get_piece.return_value = piece

        result = engine.request_move(source, target)

        self.assertTrue(result.is_accepted)
        self.assertEqual(result.reason, MoveReason.OK)
        rule_engine.validate_move.assert_called_once_with(board, source, target)
        duration_calculator.calculate.assert_called_once_with(piece, source, target)
        arbiter.start_motion.assert_called_once_with(
            piece=piece,
            source=source,
            target=target,
            duration=2000,
        )

    def test_wait_advances_arbiter_time(self):
        board = MagicMock()
        rule_engine = MagicMock()
        arbiter = MagicMock()
        duration_calculator = MagicMock()
        engine = GameEngine(
            board=board,
            rule_engine=rule_engine,
            arbiter=arbiter,
            duration_calculator=duration_calculator,
        )

        engine.wait(250)

        arbiter.advance_time.assert_called_once_with(250)

    def test_wait_sets_game_over_when_king_was_captured(self):
        board = MagicMock()
        rule_engine = MagicMock()
        arbiter = MagicMock()
        duration_calculator = MagicMock()
        arbiter.consume_captured_king_flag.return_value = True
        engine = GameEngine(
            board=board,
            rule_engine=rule_engine,
            arbiter=arbiter,
            duration_calculator=duration_calculator,
        )

        engine.wait(500)

        self.assertTrue(engine.game_over)
        arbiter.advance_time.assert_called_once_with(500)
        arbiter.consume_captured_king_flag.assert_called_once_with()

    def test_wait_keeps_game_running_when_king_was_not_captured(self):
        board = MagicMock()
        rule_engine = MagicMock()
        arbiter = MagicMock()
        duration_calculator = MagicMock()
        arbiter.consume_captured_king_flag.return_value = False
        engine = GameEngine(
            board=board,
            rule_engine=rule_engine,
            arbiter=arbiter,
            duration_calculator=duration_calculator,
        )

        engine.wait(500)

        self.assertFalse(engine.game_over)
        arbiter.advance_time.assert_called_once_with(500)
        arbiter.consume_captured_king_flag.assert_called_once_with()
