"""
Manages piece movement over time.
"""

from model.board import Board
from model.piece import Piece, PieceColor, PieceState, PieceType
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

        motion = self._active_motion

        if motion is None:
            return

        piece = motion.piece
        source = motion.source
        target = motion.target

        captured_piece = self._board.get_piece(target)
        self._last_captured_piece = None
        self._captured_king_in_last_resolution = False

        if (
            isinstance(captured_piece, Piece)
            and captured_piece.state == PieceState.AIRBORNE
        ):
            # Airborne defender captures the arriving attacker.
            self._last_captured_piece = piece
            piece.state = PieceState.CAPTURED

            if piece.type == PieceType.KING:
                self._captured_king_in_last_resolution = True

            self._board.set_piece(
                source,
                self._board.EMPTY_CELL,
            )
            captured_piece.state = PieceState.IDLE
            self._active_motion = None
            return

        if isinstance(captured_piece, Piece):
            self._last_captured_piece = captured_piece
            captured_piece.state = PieceState.CAPTURED

            if captured_piece.type == PieceType.KING:
                self._captured_king_in_last_resolution = True

        self._board.move_piece(
            source,
            target,
        )

        self._handle_promotion(piece)

        self._active_motion = None

    def _handle_promotion(
        self,
        piece: Piece,
    ) -> None:
        """
        Promotes a pawn that reaches the last rank.
        """

        if piece.type != PieceType.PAWN:
            return

        if (
            piece.color == PieceColor.WHITE
            and piece.position.row == 0
        ):
            self._promote(piece)

        elif (
            piece.color == PieceColor.BLACK
            and piece.position.row == self._board.height - 1
        ):
            self._promote(piece)

    def _promote(
        self,
        piece: Piece,
    ) -> None:
        """
        Promotes a pawn to a queen.
        """

        piece.type = PieceType.QUEEN

    def jump(
        self,
        piece: Piece,
    ) -> None:
        """
        Marks a piece as airborne.
        """

        piece.state = PieceState.AIRBORNE    