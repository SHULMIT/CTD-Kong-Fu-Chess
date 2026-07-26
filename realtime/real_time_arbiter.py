"""
Manages piece movement over time.
"""

from config.constants import JUMP_DURATION_MILLISECONDS
from events.event_bus import EventBus
from events.game_events import (
    JumpCompletedEvent,
    MoveCompletedEvent,
    ScoreChangedEvent,
)
from game.player_activity_service import PlayerActivityService
from model.board import Board
from model.piece import Piece, PieceColor, PieceState
from model.position import Position
from realtime.airborne_manager import AirborneManager
from realtime.collision_resolver import CollisionResolver
from realtime.motion import Motion
from realtime.motion_manager import MotionManager
from realtime.motion_step_planner import MotionStepPlanner
from realtime.motion_timeline import MotionTimeline
from realtime.piece_lifecycle_service import PieceLifecycleService


class RealTimeArbiter:
    """Manages real-time piece movement.

    מייצגת את רכיב השרת ``RealTimeArbiter`` ומרכזת את התנהגותו.

    Responsibility: Manages real-time piece movement.

    אחריות: מייצגת את רכיב השרת ``RealTimeArbiter`` ומרכזת את התנהגותו."""

    def __init__(
        self,
        board: Board,
        player_activity: PlayerActivityService | None = None,
    ):
        """Initialize the instance and its dependencies.

        מאתחלת את המופע ואת התלויות שלו."""
        self._board = board
        self._event_bus: EventBus | None = None
        self._player_activity = player_activity
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
        """Returns whether a motion is currently active.

        בודקת אם קיים ``active`` התנועה."""

        return self._motion_manager.has_motions()

    def get_active_motions(self) -> tuple:
        """Returns an immutable snapshot of all active motions.
                Safe for external callers — does not expose internal structure.

        מחזירה את ``active`` ``motions``."""
        return self._motion_manager.get_snapshot()

    @property
    def last_captured_piece(self) -> Piece | None:
        """Returns the last captured piece, if any.

        מבצעת את פעולת ``last`` ``captured`` הכלי."""

        return self._lifecycle.last_captured_piece

    def consume_captured_king_flag(self) -> bool:
        """Returns whether a king was captured in the last resolution,
                then resets the flag.

        מבצעת את פעולת ``consume`` ``captured`` ``king`` ``flag``."""

        return self._lifecycle.consume_captured_king_flag()

    def start_motion(
        self,
        piece: Piece,
        source: Position,
        target: Position,
        duration: int,
    ) -> None:
        """Starts a new motion.

        מתחילה את התנועה."""

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
        """Advances the active motion.

        מקדמת את הזמן."""

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
                self._publish_jump_completed(piece)

            self._cleanup_finished_motions()

    def _resolve_ready_steps(self) -> None:
        """Resolves all motions that reached a cell boundary at the current time.

        פותרת את ``ready`` ``steps``."""

        ready_motions = self._planner.get_ready_motions(
            self._motion_manager.get_all(),
        )

        for motion in ready_motions:
            if motion not in self._motion_manager.get_all():
                continue

            if not motion.is_ready_for_next_step():
                continue

            score_before = self._get_score(motion.piece.color)
            self._collision_resolver.resolve_step(motion)
            self._publish_score_change(
                player=motion.piece.color,
                previous_score=score_before,
            )

    def _cleanup_finished_motions(self) -> None:
        """Removes motions that can no longer advance.

        מבצעת את פעולת ``cleanup`` ``finished`` ``motions``."""

        for motion in list(self._motion_manager.get_all()):
            if motion.is_finished():
                self._motion_manager.remove(motion)
                if motion.current_position == motion.target:
                    self._publish_move_completed(motion)

    def jump(
        self,
        piece: Piece,
    ) -> None:
        """Marks a piece as airborne.

        מבצעת את פעולת קפיצה."""

        self._airborne_manager.jump(piece)

    def has_active_motions(self) -> bool:
        """Returns whether any motions are currently active.

        בודקת אם קיים ``active`` ``motions``."""
        return self._motion_manager.has_motions()

    def set_player_activity(
        self,
        player_activity: PlayerActivityService,
    ) -> None:
        """Connects the game activity service to capture resolution.

        מגדירה את השחקן פעילות."""
        self._collision_resolver.set_player_activity(player_activity)
        self._player_activity = player_activity

    def set_event_bus(self, event_bus: EventBus) -> None:
        """Connects this simulation to its owning game's event bus.

        מגדירה את אירוע ערוץ האירועים."""
        self._event_bus = event_bus

    @property
    def current_time(self) -> int:
        """Returns the current simulation time in milliseconds.

        מבצעת את פעולת ``current`` הזמן."""
        return self._timeline.current_time

    def _get_score(self, player: PieceColor) -> int | None:
        """Return score.

        מחזירה את התוצאה."""
        if self._player_activity is None:
            return None
        return self._player_activity.get_score(player)

    def _publish_score_change(
        self,
        player: PieceColor,
        previous_score: int | None,
    ) -> None:
        """Publish score change.

        מפרסמת את התוצאה ``change``."""
        if self._event_bus is None or self._player_activity is None:
            return

        score = self._player_activity.get_score(player)
        if previous_score == score:
            return

        self._event_bus.publish(
            ScoreChangedEvent(player=player, score=score)
        )

    def _publish_move_completed(self, motion: Motion) -> None:
        """Publish move completed.

        מפרסמת את המהלך ``completed``."""
        if self._event_bus is None:
            return
        self._event_bus.publish(
            MoveCompletedEvent(
                piece_id=motion.piece.id,
                source=motion.source,
                target=motion.target,
            )
        )

    def _publish_jump_completed(self, piece: Piece) -> None:
        """Publish jump completed.

        מפרסמת את קפיצה ``completed``."""
        if self._event_bus is None:
            return
        self._event_bus.publish(
            JumpCompletedEvent(
                piece_id=piece.id,
                position=piece.position,
            )
        )
