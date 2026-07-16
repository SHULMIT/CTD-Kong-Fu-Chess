"""
Manages piece movement over time.
"""

from config.constants import JUMP_DURATION_MILLISECONDS
from game.player_activity_service import PlayerActivityService
from model.board import Board
from model.piece import Piece, PieceState
from model.position import Position
from realtime.airborne_manager import AirborneManager
from realtime.collision_resolver import CollisionResolver
from realtime.motion import Motion
from realtime.motion_manager import MotionManager
from realtime.motion_step_planner import MotionStepPlanner
from realtime.motion_timeline import MotionTimeline
from realtime.piece_lifecycle_service import PieceLifecycleService


class RealTimeArbiter:
    """
    Manages real-time piece movement.
    """

    def __init__(
        self,
        board: Board,
        player_activity: PlayerActivityService | None = None,
    ):
        self._board = board
        self._motion_manager = MotionManager()
        self._airborne_manager = AirborneManager(
            jump_duration_milliseconds=JUMP_DURATION_MILLISECONDS,
        )
        self._timeline = MotionTimeline()
        self._planner = MotionStepPlanner()
        self._lifecycle = PieceLifecycleService(
            board=self._board,
            motion_manager=self._motion_manager,
            airborne_manager=self._airborne_manager,
        )
        self._collision_resolver = CollisionResolver(
            board=self._board,
            lifecycle=self._lifecycle,
            player_activity=player_activity,
        )
        self._motion_sequence = 0

    def has_active_motion(self) -> bool:
        """
        Returns whether a motion is currently active.
        """

        return self._motion_manager.has_motions()

    def get_active_motions(self) -> tuple:
        """
        Returns an immutable snapshot of all active motions.
        Safe for external callers — does not expose internal structure.
        """
        return self._motion_manager.get_snapshot()

    @property
    def last_captured_piece(self) -> Piece | None:
        """
        Returns the last captured piece, if any.
        """

        return self._lifecycle.last_captured_piece

    def consume_captured_king_flag(self) -> bool:
        """
        Returns whether a king was captured in the last resolution,
        then resets the flag.
        """

        return self._lifecycle.consume_captured_king_flag()

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

        motion = Motion(
            piece=piece,
            source=source,
            target=target,
            duration=duration,
            start_time=self._timeline.current_time,
            sequence=self._motion_sequence,
        )
        self._motion_sequence += 1
        piece.state = PieceState.MOVING
        self._motion_manager.add(motion)

    def advance_time(
        self,
        milliseconds: int,
    ) -> None:
        """
        Advances the active motion.
        """

        if (
            not self._motion_manager.has_motions()
            and not self._airborne_manager.has_airborne_pieces()
        ):
            return

        self._lifecycle.reset_resolution_flags()

        remaining_time = milliseconds

        while remaining_time > 0:
            next_event_time = self._timeline.next_event_delta(
                remaining_time=remaining_time,
                motions=self._motion_manager.get_all(),
                airborne_manager=self._airborne_manager,
            )

            self._timeline.advance(
                motions=self._motion_manager.get_all(),
                airborne_manager=self._airborne_manager,
                milliseconds=next_event_time,
            )
            remaining_time -= next_event_time

            self._resolve_ready_steps()

            landed_pieces = (
                self._airborne_manager
                .consume_finished_landings()
            )

            for piece in landed_pieces:
                self._lifecycle.land_piece(piece)

            self._cleanup_finished_motions()

    def _resolve_ready_steps(self) -> None:
        """
        Resolves all motions that reached a cell boundary at the current time.
        """

        ready_motions = self._planner.get_ready_motions(
            self._motion_manager.get_all(),
        )

        for motion in ready_motions:
            if motion not in self._motion_manager.get_all():
                continue

            if not motion.is_ready_for_next_step():
                continue

            self._collision_resolver.resolve_step(motion)

    def _cleanup_finished_motions(self) -> None:
        """
        Removes motions that can no longer advance.
        """

        for motion in list(self._motion_manager.get_all()):
            if motion.is_finished():
                self._motion_manager.remove(motion)

    def jump(
        self,
        piece: Piece,
    ) -> None:
        """
        Marks a piece as airborne.
        """

        self._airborne_manager.jump(piece)

    def has_active_motions(self) -> bool:
        """Returns whether any motions are currently active."""
        return self._motion_manager.has_motions()

    def set_player_activity(
        self,
        player_activity: PlayerActivityService,
    ) -> None:
        """Connects the game activity service to capture resolution."""
        self._collision_resolver.set_player_activity(player_activity)

    @property
    def current_time(self) -> int:
        """Returns the current simulation time in milliseconds."""
        return self._timeline.current_time
