"""
Manages piece lifecycle transitions in real-time simulation.
"""

from model.board import Board
from model.piece import Piece, PieceColor, PieceState, PieceType
from model.position import Position
from realtime.airborne_manager import AirborneManager
from realtime.motion_manager import MotionManager


class PieceLifecycleService:
    """
    Central place for capture, promotion, and resolution flags.

    The service keeps rule outcomes consistent regardless of who triggers them.
    """

    def __init__(
        self,
        board: Board,
        motion_manager: MotionManager,
        airborne_manager: AirborneManager,
    ):
        self._board = board
        self._motion_manager = motion_manager
        self._airborne_manager = airborne_manager
        self._last_captured_piece: Piece | None = None
        self._captured_king_in_last_resolution = False

    @property
    def last_captured_piece(self) -> Piece | None:
        return self._last_captured_piece

    def reset_resolution_flags(self) -> None:
        """
        Clears one-tick capture metadata before advancing simulation.
        """

        self._last_captured_piece = None
        self._captured_king_in_last_resolution = False

    def consume_captured_king_flag(self) -> bool:
        """
        Returns and clears king-capture flag.
        """

        captured_king = self._captured_king_in_last_resolution
        self._captured_king_in_last_resolution = False
        return captured_king

    def capture_piece(
        self,
        piece: Piece,
        position: Position,
    ) -> None:
        """
        Marks piece as captured and removes it from active systems.
        """

        self._last_captured_piece = piece
        piece.state = PieceState.CAPTURED
        self._airborne_manager.remove_piece(piece)

        if piece.type == PieceType.KING:
            self._captured_king_in_last_resolution = True

        for motion in list(self._motion_manager.get_all()):
            if motion.piece == piece:
                motion.stop()
                self._motion_manager.remove(motion)
                break

        piece_on_board = self._board.get_piece(position)
        if piece_on_board == piece:
            self._board.set_piece(position, self._board.EMPTY_CELL)

    def finalize_finished_motion_piece(
        self,
        piece: Piece,
    ) -> None:
        """
        Applies end-of-motion state transitions for the moving piece.
        """

        piece.state = PieceState.IDLE
        self._handle_promotion(piece)

    def _handle_promotion(
        self,
        piece: Piece,
    ) -> None:
        """
        Promotes pawn that reached last rank.
        """

        if piece.type != PieceType.PAWN:
            return

        if (
            piece.color == PieceColor.WHITE
            and piece.position.row == 0
        ):
            piece.type = PieceType.QUEEN
            return

        if (
            piece.color == PieceColor.BLACK
            and piece.position.row == self._board.height - 1
        ):
            piece.type = PieceType.QUEEN