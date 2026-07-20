"""
Validates chess move requests.

Responsibilities:
    - Perform general move validations.
    - Select the appropriate movement rule for each piece.
    - Delegate piece-specific validation to the matching rule.
    - Return the validation result.

This class coordinates move validation but does not implement
the movement logic of individual chess pieces.
"""

from model.board import Board
from model.position import Position
from model.piece import Piece, PieceType

from game.move_reason import MoveReason
from rules.move_validation import MoveValidation
from rules.movement_rule import MovementRule

from rules.rook_rule import RookRule
from rules.bishop_rule import BishopRule
from rules.queen_rule import QueenRule
from rules.knight_rule import KnightRule
from rules.king_rule import KingRule
from rules.pawn_rule import PawnRule


class RuleEngine:
    """
    Validates moves using the appropriate movement rule.
    """

    _RULES = {
        PieceType.ROOK: RookRule(),
        PieceType.BISHOP: BishopRule(),
        PieceType.QUEEN: QueenRule(),
        PieceType.KNIGHT: KnightRule(),
        PieceType.KING: KingRule(),
        PieceType.PAWN: PawnRule(),
    }

    def validate_move(
        self,
        board: Board,
        source: Position,
        target: Position,
    ) -> MoveValidation:
        """
        Returns whether a move is legal.
        """

        validation = self._validate_basic_rules(
            board,
            source,
            target,
        )

        if validation is not None:
            return validation

        piece = board.get_piece(source)

        legal_moves = self.get_legal_moves(
            board,
            piece,
        )

        if target in legal_moves:
            return MoveValidation(
                is_valid=True,
                reason=MoveReason.OK,
            )

        return MoveValidation(
            is_valid=False,
            reason=MoveReason.ILLEGAL_PIECE_MOVE,
        )

    def get_legal_moves(
        self,
        board: Board,
        piece: Piece,
    ) -> set[Position]:
        """
        Returns every legal destination for the given piece.
        """

        rule = self._get_rule(piece.type)

        return rule.get_legal_moves(
            piece,
            board,
        )

    def _get_rule(
        self,
        piece_type: PieceType,
    ) -> MovementRule:
        """
        Returns the movement rule matching the given piece type.
        """

        return self._RULES[piece_type]

    def _validate_basic_rules(
        self,
        board: Board,
        source: Position,
        target: Position,
    ) -> MoveValidation | None:
        """
        Performs validations that are independent of piece movement.
        """

        if not board.is_inside(source):
            return MoveValidation(
                is_valid=False,
                reason=MoveReason.OUTSIDE_BOARD,
            )

        if not board.is_inside(target):
            return MoveValidation(
                is_valid=False,
                reason=MoveReason.OUTSIDE_BOARD,
            )

        piece = board.get_piece(source)

        if piece is None or piece == board.EMPTY_CELL:
            return MoveValidation(
                is_valid=False,
                reason=MoveReason.EMPTY_SOURCE,
            )

        target_piece = board.get_piece(target)

        if (
            target_piece is not None
            and target_piece != board.EMPTY_CELL
            and target_piece.color == piece.color
        ):
            return MoveValidation(
                is_valid=False,
                reason=MoveReason.FRIENDLY_DESTINATION,
            )

        return None
