"""
Tests for RuleEngine validation logic.
"""

import unittest

from config.constants import BOARD_SIZE
from model.board import Board
from model.piece import Piece, PieceColor, PieceType, PieceState
from model.position import Position
from rules.rule_engine import RuleEngine
from rules.move_reason import MoveReason


class TestRuleEngineValidation(unittest.TestCase):
    """Tests for RuleEngine.validate_move()"""

    def setUp(self):
        """Set up a fresh board and engine for each test."""
        self.engine = RuleEngine()
        # Create a standard board with None in each cell
        self.board = Board([
            [None for _ in range(BOARD_SIZE)]
            for _ in range(BOARD_SIZE)
        ])

    def test_move_outside_board_source(self):
        """Test that moves from outside the board are rejected."""
        source = Position(-1, 0)
        target = Position(0, 0)

        result = self.engine.validate_move(self.board, source, target)

        self.assertFalse(result.is_valid)
        self.assertEqual(result.reason, MoveReason.OUTSIDE_BOARD)

    def test_move_outside_board_target(self):
        """Test that moves to outside the board are rejected."""
        piece = Piece(
            piece_id=1,
            piece_type=PieceType.ROOK,
            color=PieceColor.WHITE,
            position=Position(0, 0),
            state=PieceState.IDLE,
        )
        self.board.set_piece(Position(0, 0), piece)

        source = Position(0, 0)
        target = Position(10, 0)

        result = self.engine.validate_move(self.board, source, target)

        self.assertFalse(result.is_valid)
        self.assertEqual(result.reason, MoveReason.OUTSIDE_BOARD)

    def test_move_from_empty_square(self):
        """Test that moves from empty squares are rejected."""
        source = Position(0, 0)
        target = Position(0, 1)

        result = self.engine.validate_move(self.board, source, target)

        self.assertFalse(result.is_valid)
        self.assertEqual(result.reason, MoveReason.EMPTY_SOURCE)

    def test_move_to_friendly_piece(self):
        """Test that capturing friendly pieces is rejected."""
        white_rook = Piece(
            piece_id=1,
            piece_type=PieceType.ROOK,
            color=PieceColor.WHITE,
            position=Position(0, 0),
            state=PieceState.IDLE,
        )
        white_pawn = Piece(
            piece_id=2,
            piece_type=PieceType.PAWN,
            color=PieceColor.WHITE,
            position=Position(0, 1),
            state=PieceState.IDLE,
        )
        self.board.set_piece(Position(0, 0), white_rook)
        self.board.set_piece(Position(0, 1), white_pawn)

        source = Position(0, 0)
        target = Position(0, 1)

        result = self.engine.validate_move(self.board, source, target)

        self.assertFalse(result.is_valid)
        self.assertEqual(result.reason, MoveReason.FRIENDLY_DESTINATION)

    def test_valid_rook_move_horizontal(self):
        """Test that valid rook horizontal moves are accepted."""
        rook = Piece(
            piece_id=1,
            piece_type=PieceType.ROOK,
            color=PieceColor.WHITE,
            position=Position(0, 0),
            state=PieceState.IDLE,
        )
        self.board.set_piece(Position(0, 0), rook)

        source = Position(0, 0)
        target = Position(0, 3)

        result = self.engine.validate_move(self.board, source, target)

        self.assertTrue(result.is_valid)
        self.assertEqual(result.reason, MoveReason.OK)

    def test_valid_rook_move_vertical(self):
        """Test that valid rook vertical moves are accepted."""
        rook = Piece(
            piece_id=1,
            piece_type=PieceType.ROOK,
            color=PieceColor.WHITE,
            position=Position(0, 0),
            state=PieceState.IDLE,
        )
        self.board.set_piece(Position(0, 0), rook)

        source = Position(0, 0)
        target = Position(5, 0)

        result = self.engine.validate_move(self.board, source, target)

        self.assertTrue(result.is_valid)
        self.assertEqual(result.reason, MoveReason.OK)

    def test_invalid_rook_move_diagonal(self):
        """Test that invalid rook diagonal moves are rejected."""
        rook = Piece(
            piece_id=1,
            piece_type=PieceType.ROOK,
            color=PieceColor.WHITE,
            position=Position(0, 0),
            state=PieceState.IDLE,
        )
        self.board.set_piece(Position(0, 0), rook)

        source = Position(0, 0)
        target = Position(3, 3)

        result = self.engine.validate_move(self.board, source, target)

        self.assertFalse(result.is_valid)
        self.assertEqual(result.reason, MoveReason.ILLEGAL_PIECE_MOVE)

    def test_valid_bishop_move(self):
        """Test that valid bishop diagonal moves are accepted."""
        bishop = Piece(
            piece_id=1,
            piece_type=PieceType.BISHOP,
            color=PieceColor.WHITE,
            position=Position(0, 0),
            state=PieceState.IDLE,
        )
        self.board.set_piece(Position(0, 0), bishop)

        source = Position(0, 0)
        target = Position(3, 3)

        result = self.engine.validate_move(self.board, source, target)

        self.assertTrue(result.is_valid)
        self.assertEqual(result.reason, MoveReason.OK)

    def test_invalid_bishop_move_horizontal(self):
        """Test that invalid bishop horizontal moves are rejected."""
        bishop = Piece(
            piece_id=1,
            piece_type=PieceType.BISHOP,
            color=PieceColor.WHITE,
            position=Position(0, 0),
            state=PieceState.IDLE,
        )
        self.board.set_piece(Position(0, 0), bishop)

        source = Position(0, 0)
        target = Position(0, 3)

        result = self.engine.validate_move(self.board, source, target)

        self.assertFalse(result.is_valid)
        self.assertEqual(result.reason, MoveReason.ILLEGAL_PIECE_MOVE)

    def test_valid_queen_move_horizontal(self):
        """Test that valid queen horizontal moves are accepted."""
        queen = Piece(
            piece_id=1,
            piece_type=PieceType.QUEEN,
            color=PieceColor.WHITE,
            position=Position(0, 0),
            state=PieceState.IDLE,
        )
        self.board.set_piece(Position(0, 0), queen)

        source = Position(0, 0)
        target = Position(0, 5)

        result = self.engine.validate_move(self.board, source, target)

        self.assertTrue(result.is_valid)
        self.assertEqual(result.reason, MoveReason.OK)

    def test_valid_queen_move_diagonal(self):
        """Test that valid queen diagonal moves are accepted."""
        queen = Piece(
            piece_id=1,
            piece_type=PieceType.QUEEN,
            color=PieceColor.WHITE,
            position=Position(0, 0),
            state=PieceState.IDLE,
        )
        self.board.set_piece(Position(0, 0), queen)

        source = Position(0, 0)
        target = Position(4, 4)

        result = self.engine.validate_move(self.board, source, target)

        self.assertTrue(result.is_valid)
        self.assertEqual(result.reason, MoveReason.OK)

    def test_valid_knight_move(self):
        """Test that valid knight L-shaped moves are accepted."""
        knight = Piece(
            piece_id=1,
            piece_type=PieceType.KNIGHT,
            color=PieceColor.WHITE,
            position=Position(0, 0),
            state=PieceState.IDLE,
        )
        self.board.set_piece(Position(0, 0), knight)

        source = Position(0, 0)
        target = Position(2, 1)

        result = self.engine.validate_move(self.board, source, target)

        self.assertTrue(result.is_valid)
        self.assertEqual(result.reason, MoveReason.OK)

    def test_invalid_knight_move(self):
        """Test that invalid knight moves are rejected."""
        knight = Piece(
            piece_id=1,
            piece_type=PieceType.KNIGHT,
            color=PieceColor.WHITE,
            position=Position(0, 0),
            state=PieceState.IDLE,
        )
        self.board.set_piece(Position(0, 0), knight)

        source = Position(0, 0)
        target = Position(0, 3)

        result = self.engine.validate_move(self.board, source, target)

        self.assertFalse(result.is_valid)
        self.assertEqual(result.reason, MoveReason.ILLEGAL_PIECE_MOVE)

    def test_valid_king_move(self):
        """Test that valid king one-step moves are accepted."""
        king = Piece(
            piece_id=1,
            piece_type=PieceType.KING,
            color=PieceColor.WHITE,
            position=Position(0, 0),
            state=PieceState.IDLE,
        )
        self.board.set_piece(Position(0, 0), king)

        source = Position(0, 0)
        target = Position(1, 1)

        result = self.engine.validate_move(self.board, source, target)

        self.assertTrue(result.is_valid)
        self.assertEqual(result.reason, MoveReason.OK)

    def test_invalid_king_move_two_steps(self):
        """Test that invalid king multi-step moves are rejected."""
        king = Piece(
            piece_id=1,
            piece_type=PieceType.KING,
            color=PieceColor.WHITE,
            position=Position(0, 0),
            state=PieceState.IDLE,
        )
        self.board.set_piece(Position(0, 0), king)

        source = Position(0, 0)
        target = Position(2, 0)

        result = self.engine.validate_move(self.board, source, target)

        self.assertFalse(result.is_valid)
        self.assertEqual(result.reason, MoveReason.ILLEGAL_PIECE_MOVE)

    def test_valid_white_pawn_move(self):
        """Test that valid white pawn forward moves are accepted."""
        pawn = Piece(
            piece_id=1,
            piece_type=PieceType.PAWN,
            color=PieceColor.WHITE,
            position=Position(6, 0),
            state=PieceState.IDLE,
        )
        self.board.set_piece(Position(6, 0), pawn)

        source = Position(6, 0)
        target = Position(5, 0)

        result = self.engine.validate_move(self.board, source, target)

        self.assertTrue(result.is_valid)
        self.assertEqual(result.reason, MoveReason.OK)

    def test_valid_black_pawn_move(self):
        """Test that valid black pawn forward moves are accepted."""
        pawn = Piece(
            piece_id=1,
            piece_type=PieceType.PAWN,
            color=PieceColor.BLACK,
            position=Position(1, 0),
            state=PieceState.IDLE,
        )
        self.board.set_piece(Position(1, 0), pawn)

        source = Position(1, 0)
        target = Position(2, 0)

        result = self.engine.validate_move(self.board, source, target)

        self.assertTrue(result.is_valid)
        self.assertEqual(result.reason, MoveReason.OK)

    def test_invalid_pawn_move_backward(self):
        """Test that pawn backward moves are rejected."""
        pawn = Piece(
            piece_id=1,
            piece_type=PieceType.PAWN,
            color=PieceColor.WHITE,
            position=Position(3, 0),
            state=PieceState.IDLE,
        )
        self.board.set_piece(Position(3, 0), pawn)

        source = Position(3, 0)
        target = Position(4, 0)

        result = self.engine.validate_move(self.board, source, target)

        self.assertFalse(result.is_valid)
        self.assertEqual(result.reason, MoveReason.ILLEGAL_PIECE_MOVE)

    def test_valid_capture_enemy_piece(self):
        """Test that capturing enemy pieces is allowed."""
        white_rook = Piece(
            piece_id=1,
            piece_type=PieceType.ROOK,
            color=PieceColor.WHITE,
            position=Position(0, 0),
            state=PieceState.IDLE,
        )
        black_rook = Piece(
            piece_id=2,
            piece_type=PieceType.ROOK,
            color=PieceColor.BLACK,
            position=Position(0, 5),
            state=PieceState.IDLE,
        )
        self.board.set_piece(Position(0, 0), white_rook)
        self.board.set_piece(Position(0, 5), black_rook)

        source = Position(0, 0)
        target = Position(0, 5)

        result = self.engine.validate_move(self.board, source, target)

        self.assertTrue(result.is_valid)
        self.assertEqual(result.reason, MoveReason.OK)

    def test_get_legal_moves_rook(self):
        """Test that get_legal_moves returns correct set for rook."""
        rook = Piece(
            piece_id=1,
            piece_type=PieceType.ROOK,
            color=PieceColor.WHITE,
            position=Position(0, 0),
            state=PieceState.IDLE,
        )
        self.board.set_piece(Position(0, 0), rook)

        legal_moves = self.engine.get_legal_moves(self.board, rook)

        # Rook at (0, 0) should have 14 legal moves (7 horizontal + 7 vertical)
        self.assertEqual(len(legal_moves), 14)

    def test_get_legal_moves_knight(self):
        """Test that get_legal_moves returns correct set for knight."""
        knight = Piece(
            piece_id=1,
            piece_type=PieceType.KNIGHT,
            color=PieceColor.WHITE,
            position=Position(3, 3),
            state=PieceState.IDLE,
        )
        self.board.set_piece(Position(3, 3), knight)

        legal_moves = self.engine.get_legal_moves(self.board, knight)

        # Knight in center should have 8 legal moves
        self.assertEqual(len(legal_moves), 8)


if __name__ == "__main__":
    unittest.main()
