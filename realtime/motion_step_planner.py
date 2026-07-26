"""
Selects and orders motions that are ready to step.
"""

from realtime.motion import Motion


class MotionStepPlanner:
    """Chooses which motions should resolve in the current tick.

        Ordering rule:
        older arrivals resolve first so later arrivals can override them.

    מייצגת את רכיב השרת ``MotionStepPlanner`` ומרכזת את התנהגותו.

    Responsibility: Chooses which motions should resolve in the current tick.

    אחריות: מייצגת את רכיב השרת ``MotionStepPlanner`` ומרכזת את התנהגותו."""

    def get_ready_motions(
        self,
        motions: list[Motion],
    ) -> list[Motion]:
        """Returns motions that reached a cell boundary, sorted by arrival order.

        מחזירה את ``ready`` ``motions``."""

        ready_motions = [
            motion
            for motion in motions
            if motion.is_ready_for_next_step()
        ]

        ready_motions.sort(
            key=lambda motion: (
                motion.start_time,
                motion.sequence,
            )
        )

        return ready_motions