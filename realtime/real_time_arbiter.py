"""
Manages piece movement over time.
"""

from model.board import Board
from model.piece import Piece, PieceState, PieceType
from model.position import Position
from realtime.motion import Motion


class RealTimeArbiter:
    """
    Manages real-time piece movement.
    """

    def __init__(
        self,
        board: Board,
    ):
        self._board = board
        self._active_motion: Motion | None = None
        self._last_captured_piece: Piece | None = None
        self._captured_king_in_last_resolution = False

    def has_active_motion(self) -> bool:
        """
        Returns whether a motion is currently active.
        """

        return self._active_motion is not None

    @property
    def last_captured_piece(self) -> Piece | None:
        """
        Returns the last captured piece, if any.
        """

        return self._last_captured_piece

    def consume_captured_king_flag(self) -> bool:
        """
        Returns whether a king was captured in the last resolution,
        then resets the flag.
        """

        captured_king = self._captured_king_in_last_resolution
        self._captured_king_in_last_resolution = False
        return captured_king

    def start_motion(
        self,
        piece: Piece,
        source: Position,
        target: Position,
        duration: int,
    ) -> None:
        """
        Starts a new motion.
        """

        self._active_motion = Motion(
            piece=piece,
            source=source,
            target=target,
            duration=duration,
        )

    def advance_time(
        self,
        milliseconds: int,
    ) -> None:
        """
        Advances the active motion.
        """

        if self._active_motion is None:
            return

        self._active_motion.advance_time(milliseconds)

        if self._active_motion.is_finished():
            self._resolve_arrival()

    def _resolve_arrival(self) -> None:
        """
        Resolves the completed motion.
        """

        source = self._active_motion.source
        target = self._active_motion.target

        captured_piece = self._board.get_piece(target)
        self._last_captured_piece = None
        self._captured_king_in_last_resolution = False

        if captured_piece != self._board.EMPTY_CELL:
            self._last_captured_piece = captured_piece

            if isinstance(captured_piece, Piece):
                captured_piece.state = PieceState.CAPTURED

                if captured_piece.type == PieceType.KING:
                    self._captured_king_in_last_resolution = True

        self._board.move_piece(
            source,
            target,
        )

        self._active_motion = None