"""
Shared helper functions for movement rules.
"""

from model.board import Board
from model.piece import Piece
from model.position import Position


ORTHOGONAL_DIRECTIONS = (
    (-1, 0),
    (1, 0),
    (0, -1),
    (0, 1),
)

DIAGONAL_DIRECTIONS = (
    (-1, -1),
    (-1, 1),
    (1, -1),
    (1, 1),
)


def is_empty_square(piece: Piece | None) -> bool:
    return piece is None or piece == Board.EMPTY_CELL


def is_enemy_piece(
    moving_piece: Piece,
    target_piece: Piece | None,
) -> bool:
    return (
        isinstance(target_piece, Piece)
        and moving_piece.color != target_piece.color
    )


def is_friendly_piece(
    moving_piece: Piece,
    target_piece: Piece | None,
) -> bool:
    return (
        isinstance(target_piece, Piece)
        and moving_piece.color == target_piece.color
    )


def collect_moves_in_direction(
    board: Board,
    piece: Piece,
    row_step: int,
    column_step: int,
) -> set[Position]:
    legal_moves = set()

    current_position = piece.position.offset(row_step, column_step)

    while board.is_inside(current_position):
        target_piece = board.get_piece(current_position)

        if is_empty_square(target_piece):
            legal_moves.add(current_position)

        elif is_enemy_piece(piece, target_piece):
            legal_moves.add(current_position)
            break

        else:
            break

        current_position = current_position.offset(row_step, column_step)

    return legal_moves