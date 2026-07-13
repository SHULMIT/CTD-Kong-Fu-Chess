"""
Tests for game.game_state_service.
"""

from unittest.mock import MagicMock
import unittest

from game.game_state_service import GameStateService


class TestGameStateService(unittest.TestCase):
    def test_game_over_defaults_to_false(self):
        arbiter = MagicMock()
        service = GameStateService(arbiter=arbiter)

        self.assertFalse(service.game_over)

    def test_wait_sets_game_over_when_king_was_captured(self):
        arbiter = MagicMock()
        arbiter.consume_captured_king_flag.return_value = True
        service = GameStateService(arbiter=arbiter)

        service.wait(500)

        self.assertTrue(service.game_over)
        arbiter.advance_time.assert_called_once_with(500)
        arbiter.consume_captured_king_flag.assert_called_once_with()

    def test_wait_keeps_game_running_when_king_not_captured(self):
        arbiter = MagicMock()
        arbiter.consume_captured_king_flag.return_value = False
        service = GameStateService(arbiter=arbiter)

        service.wait(250)

        self.assertFalse(service.game_over)
        arbiter.advance_time.assert_called_once_with(250)
        arbiter.consume_captured_king_flag.assert_called_once_with()

    def test_jump_piece_delegates_to_arbiter(self):
        arbiter = MagicMock()
        piece = MagicMock()
        service = GameStateService(arbiter=arbiter)

        service.jump_piece(piece)

        arbiter.jump.assert_called_once_with(piece)