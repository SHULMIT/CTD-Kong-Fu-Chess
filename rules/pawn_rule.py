"""
Movement rule for the pawn.
"""

from model.board import Board
from model.piece import Piece, PieceColor
from model.position import Position

from rules.movement_rule import MovementRule
from rules.movement_utils import (
    is_empty_square,
    is_enemy_piece,
)


class PawnRule(MovementRule):
    """Calculates every legal move for a pawn.

    מייצגת את רכיב השרת ``PawnRule`` ומרכזת את התנהגותו.

    Responsibility: Calculates every legal move for a pawn.

    אחריות: מייצגת את רכיב השרת ``PawnRule`` ומרכזת את התנהגותו."""

    SINGLE_STEP = 1
    DOUBLE_STEP = 2

    WHITE_DIRECTION = -1
    BLACK_DIRECTION = 1

    def get_legal_moves(
        self,
        piece: Piece,
        board: Board,
    ) -> set[Position]:
        """Returns every legal destination for the pawn.

        מחזירה את ``legal`` המהלכים."""

        legal_moves = set()

        direction = self._move_direction(piece)
        start_row = self._starting_row(piece, board)

        self._add_forward_move(
            board,
            piece,
            direction,
            legal_moves,
        )

        self._add_double_move(
            board,
            piece,
            direction,
            start_row,
            legal_moves,
        )

        self._add_diagonal_captures(
            board,
            piece,
            direction,
            legal_moves,
        )

        return legal_moves

    def _move_direction(
        self,
        piece: Piece,
    ) -> int:
        """Returns the pawn movement direction.

        מזיזה את ``direction``."""

        if piece.color == PieceColor.WHITE:
            return self.WHITE_DIRECTION

        return self.BLACK_DIRECTION

    def _starting_row(
        self,
        piece: Piece,
        board: Board,
    ) -> int:
        """Returns the pawn starting row.

        מבצעת את פעולת ``starting`` ``row``."""

        if piece.color == PieceColor.WHITE:
            return board.height - 2

        return 1

    def _add_forward_move(
        self,
        board: Board,
        piece: Piece,
        direction: int,
        legal_moves: set[Position],
    ):
        """Adds the single forward move if legal.

        מוסיפה את ``forward`` המהלך."""

        position = piece.position.offset(direction, 0)

        if not board.is_inside(position):
            return

        if is_empty_square(board.get_piece(position)):
            legal_moves.add(position)

    def _add_double_move(
        self,
        board: Board,
        piece: Piece,
        direction: int,
        start_row: int,
        legal_moves: set[Position],
    ):
        """Adds the double forward move if legal.

        מוסיפה את ``double`` המהלך."""

        if piece.position.row != start_row:
            return

        middle = piece.position.offset(direction, 0)
        target = piece.position.offset(
            direction * self.DOUBLE_STEP,
            0,
        )

        if not board.is_inside(target):
            return

        if (
            is_empty_square(board.get_piece(middle))
            and
            is_empty_square(board.get_piece(target))
        ):
            legal_moves.add(target)

    def _add_diagonal_captures(
        self,
        board: Board,
        piece: Piece,
        direction: int,
        legal_moves: set[Position],
    ):
        """Adds every legal diagonal capture.

        מוסיפה את ``diagonal`` ``captures``."""

        for column_offset in (-1, 1):

            position = piece.position.offset(
                direction,
                column_offset,
            )

            if not board.is_inside(position):
                continue

            target_piece = board.get_piece(position)

            if is_enemy_piece(piece, target_piece):
                legal_moves.add(position)
