"""Integration tests for end-to-end game flow components."""

import unittest

from board_io.text_board_parser import TextBoardParser
from game.game_engine import GameEngine
from model.position import Position
from realtime.duration_calculator import DurationCalculator
from realtime.real_time_arbiter import RealTimeArbiter
from rules.rule_engine import RuleEngine


class TestFullSystemFlow(unittest.TestCase):
    def _build_engine(self, board_lines: list[str]) -> GameEngine:
        board = TextBoardParser.parse(board_lines)
        return GameEngine(
            board=board,
            rule_engine=RuleEngine(),
            arbiter=RealTimeArbiter(board),
            duration_calculator=DurationCalculator(),
        )

    def test_request_move_then_wait_moves_piece_on_arrival(self):
        engine = self._build_engine([
            "wR . . .",
        ])

        source = Position(0, 0)
        target = Position(0, 3)

        result = engine.request_move(source, target)

        self.assertTrue(result.is_accepted)
        self.assertIsNotNone(engine.get_piece(source))

        engine.wait(2000)
        self.assertIsNotNone(engine.get_piece(source))

        engine.wait(1000)
        self.assertEqual(engine.get_piece(source), engine.board.EMPTY_CELL)
        self.assertIsNotNone(engine.get_piece(target))

    def test_capturing_king_sets_game_over_after_wait(self):
        engine = self._build_engine([
            "wR bK . .",
        ])

        source = Position(0, 0)
        target = Position(0, 1)

        result = engine.request_move(source, target)

        self.assertTrue(result.is_accepted)
        self.assertFalse(engine.game_over)

        engine.wait(1000)

        self.assertTrue(engine.game_over)
