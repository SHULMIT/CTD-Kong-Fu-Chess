"""
Resolves a single motion step against board occupancy and collision rules.
"""

from model.board import Board
from model.piece import Piece, PieceState
from realtime.motion import Motion
from realtime.piece_lifecycle_service import PieceLifecycleService


class CollisionResolver:
    """
    Applies the collision policy for one motion step.

    Rules encoded here:
    - Later enemy arrival captures earlier arrival on same square.
    - Later friendly arrival gets stuck on previous square.
    - Airborne defender captures the arriving attacker.
    """

    def __init__(
        self,
        board: Board,
        lifecycle: PieceLifecycleService,
    ):
        self._board = board
        self._lifecycle = lifecycle

    def resolve_step(
        self,
        motion: Motion,
    ) -> None:
        """
        Resolves one potential cell transition for the given motion.
        """

        moving_piece = motion.piece
        source_position = motion.current_position
        target_position = motion.next_position

        if target_position is None:
            motion.stop()
            return

        target_piece = self._board.get_piece(target_position)

        if isinstance(target_piece, Piece):
            if target_piece.state == PieceState.AIRBORNE:
                self._lifecycle.capture_piece(
                    piece=moving_piece,
                    position=source_position,
                )
                motion.stop()
                return

            if moving_piece.color == target_piece.color:
                moving_piece.state = PieceState.IDLE
                motion.stop()
                return

            self._lifecycle.capture_piece(
                piece=target_piece,
                position=target_position,
            )

        self._board.set_piece(source_position, self._board.EMPTY_CELL)
        self._board.set_piece(target_position, moving_piece)
        moving_piece.position = target_position
        motion.step_forward()

        if motion.is_finished():
            self._lifecycle.finalize_finished_motion_piece(moving_piece)