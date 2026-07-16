"""
Tests for realtime.real_time_arbiter.
"""

import unittest

from config.constants import EMPTY_SQUARE
from model.board import Board
from model.piece import Piece, PieceColor, PieceState, PieceType
from model.position import Position
from realtime.real_time_arbiter import RealTimeArbiter


class TestRealTimeArbiter(unittest.TestCase):
    def _make_piece(
        self,
        piece_id: int,
        piece_type: PieceType,
        row: int,
        column: int,
        color: PieceColor = PieceColor.WHITE,
    ) -> Piece:
        return Piece(
            piece_id=piece_id,
            piece_type=piece_type,
            color=color,
            position=Position(row, column),
            state=PieceState.IDLE,
        )

    def test_capture_marks_piece_as_captured_and_stores_last_captured_piece(self):
        attacker = self._make_piece(1, PieceType.ROOK, 0, 0, PieceColor.WHITE)
        victim = self._make_piece(2, PieceType.BISHOP, 0, 1, PieceColor.BLACK)
        board = Board([[attacker, victim]])
        arbiter = RealTimeArbiter(board=board)

        arbiter.start_motion(
            piece=attacker,
            source=Position(0, 0),
            target=Position(0, 1),
            duration=1000,
        )
        arbiter.advance_time(1000)

        self.assertEqual(victim.state, PieceState.CAPTURED)
        self.assertIs(arbiter.last_captured_piece, victim)
        self.assertIs(board.get_piece(Position(0, 1)), attacker)
        self.assertEqual(board.get_piece(Position(0, 0)), EMPTY_SQUARE)

    def test_consume_captured_king_flag_returns_true_once_then_resets(self):
        attacker = self._make_piece(1, PieceType.QUEEN, 0, 0, PieceColor.WHITE)
        king = self._make_piece(2, PieceType.KING, 0, 1, PieceColor.BLACK)
        board = Board([[attacker, king]])
        arbiter = RealTimeArbiter(board=board)

        arbiter.start_motion(
            piece=attacker,
            source=Position(0, 0),
            target=Position(0, 1),
            duration=1000,
        )
        arbiter.advance_time(1000)

        self.assertTrue(arbiter.consume_captured_king_flag())
        self.assertFalse(arbiter.consume_captured_king_flag())

    def test_non_capture_keeps_last_captured_none_and_king_flag_false(self):
        mover = self._make_piece(1, PieceType.ROOK, 0, 0, PieceColor.WHITE)
        board = Board([[mover, EMPTY_SQUARE]])
        arbiter = RealTimeArbiter(board=board)

        arbiter.start_motion(
            piece=mover,
            source=Position(0, 0),
            target=Position(0, 1),
            duration=1000,
        )
        arbiter.advance_time(1000)

        self.assertIsNone(arbiter.last_captured_piece)
        self.assertFalse(arbiter.consume_captured_king_flag())

    def test_has_active_motion_transitions_true_to_false_on_finish(self):
        mover = self._make_piece(1, PieceType.KNIGHT, 0, 0, PieceColor.WHITE)
        board = Board([[mover, EMPTY_SQUARE, EMPTY_SQUARE]])
        arbiter = RealTimeArbiter(board=board)

        arbiter.start_motion(
            piece=mover,
            source=Position(0, 0),
            target=Position(0, 2),
            duration=1000,
        )

        self.assertTrue(arbiter.has_active_motion())

        arbiter.advance_time(1000)

        self.assertFalse(arbiter.has_active_motion())

    def test_arriving_attacker_captures_airborne_defender(self):
        defender = self._make_piece(1, PieceType.KING, 1, 0, PieceColor.WHITE)
        attacker = self._make_piece(2, PieceType.ROOK, 1, 1, PieceColor.BLACK)
        board = Board(
            [
                [EMPTY_SQUARE, EMPTY_SQUARE, EMPTY_SQUARE],
                [defender, attacker, EMPTY_SQUARE],
                [EMPTY_SQUARE, EMPTY_SQUARE, EMPTY_SQUARE],
            ]
        )
        arbiter = RealTimeArbiter(board=board)

        arbiter.jump(defender)
        arbiter.start_motion(
            piece=attacker,
            source=Position(1, 1),
            target=Position(1, 0),
            duration=1000,
        )
        arbiter.advance_time(1000)

        self.assertIs(board.get_piece(Position(1, 0)), attacker)
        self.assertEqual(board.get_piece(Position(1, 1)), EMPTY_SQUARE)
        self.assertEqual(defender.state, PieceState.CAPTURED)
        self.assertEqual(attacker.state, PieceState.IDLE)
        self.assertIs(arbiter.last_captured_piece, defender)
        self.assertTrue(arbiter.consume_captured_king_flag())

    def test_jump_lands_after_one_second(self):
        jumper = self._make_piece(1, PieceType.KING, 0, 0, PieceColor.WHITE)
        board = Board([[jumper]])
        arbiter = RealTimeArbiter(board=board)

        arbiter.jump(jumper)
        arbiter.advance_time(999)

        self.assertEqual(jumper.state, PieceState.AIRBORNE)

        arbiter.advance_time(1)

        self.assertEqual(jumper.state, PieceState.IDLE)

    def test_enemy_arrives_after_landing_captures_normally(self):
        defender = self._make_piece(1, PieceType.KING, 0, 0, PieceColor.WHITE)
        attacker = self._make_piece(2, PieceType.ROOK, 0, 3, PieceColor.BLACK)
        board = Board([[defender, EMPTY_SQUARE, EMPTY_SQUARE, attacker]])
        arbiter = RealTimeArbiter(board=board)

        arbiter.jump(defender)
        arbiter.start_motion(
            piece=attacker,
            source=Position(0, 3),
            target=Position(0, 0),
            duration=3000,
        )
        arbiter.advance_time(3000)

        self.assertIs(board.get_piece(Position(0, 0)), attacker)
        self.assertEqual(defender.state, PieceState.CAPTURED)
        self.assertEqual(attacker.state, PieceState.IDLE)
        self.assertIs(arbiter.last_captured_piece, defender)
        self.assertTrue(arbiter.consume_captured_king_flag())

    def test_later_enemy_arrival_captures_earlier_arrival_on_same_square(self):
        white_rook = self._make_piece(1, PieceType.ROOK, 0, 0, PieceColor.WHITE)
        black_rook = self._make_piece(2, PieceType.ROOK, 0, 4, PieceColor.BLACK)
        board = Board([[white_rook, EMPTY_SQUARE, EMPTY_SQUARE, EMPTY_SQUARE, black_rook]])
        arbiter = RealTimeArbiter(board=board)

        arbiter.start_motion(
            piece=white_rook,
            source=Position(0, 0),
            target=Position(0, 2),
            duration=2000,
        )

        arbiter.advance_time(1000)

        arbiter.start_motion(
            piece=black_rook,
            source=Position(0, 4),
            target=Position(0, 2),
            duration=2000,
        )

        arbiter.advance_time(2000)

        self.assertIs(board.get_piece(Position(0, 2)), black_rook)
        self.assertEqual(white_rook.state, PieceState.CAPTURED)
        self.assertIs(arbiter.last_captured_piece, white_rook)

    def test_later_friendly_arrival_gets_stuck_on_almost_collision(self):
        rook = self._make_piece(1, PieceType.ROOK, 7, 4, PieceColor.WHITE)
        queen = self._make_piece(2, PieceType.QUEEN, 4, 0, PieceColor.WHITE)

        board_rows = [
            [EMPTY_SQUARE for _ in range(8)]
            for _ in range(8)
        ]
        board_rows[7][4] = rook
        board_rows[4][0] = queen
        board = Board(board_rows)

        arbiter = RealTimeArbiter(board=board)

        arbiter.start_motion(
            piece=queen,
            source=Position(4, 0),
            target=Position(4, 7),
            duration=7000,
        )

        arbiter.advance_time(1000)

        arbiter.start_motion(
            piece=rook,
            source=Position(7, 4),
            target=Position(0, 4),
            duration=7000,
        )

        arbiter.advance_time(7000)

        self.assertIs(board.get_piece(Position(5, 4)), rook)
        self.assertIs(board.get_piece(Position(4, 7)), queen)
        self.assertEqual(rook.state, PieceState.IDLE)
