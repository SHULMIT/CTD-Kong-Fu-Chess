"""
Represents a single active piece movement.
"""

from math import ceil

from model.piece import Piece
from model.piece import PieceType
from model.position import Position


class Motion:
    """Represents a single active movement.

    מייצגת את רכיב השרת ``Motion`` ומרכזת את התנהגותו.

    Responsibility: Represents a single active movement.

    אחריות: מייצגת את רכיב השרת ``Motion`` ומרכזת את התנהגותו."""

    def __init__(
        self,
        piece: Piece,
        source: Position,
        target: Position,
        duration: int,
        start_time: int,
        sequence: int,
    ):
        """Initialize the instance and its dependencies.

        מאתחלת את המופע ואת התלויות שלו."""
        self._piece = piece
        self._source = source
        self._target = target
        self._duration = duration
        self._elapsed_time = 0
        self._start_time = start_time
        self._sequence = sequence
        self._path = self._build_path(
            piece_type=piece.type,
            source=source,
            target=target,
        )
        self._current_index = 0
        self._is_stopped = False

    @property
    def piece(self) -> Piece:
        """Perform the piece operation.

        מבצעת את פעולת הכלי."""
        return self._piece

    @property
    def source(self) -> Position:
        """Perform the source operation.

        מבצעת את פעולת המקור."""
        return self._source

    @property
    def target(self) -> Position:
        """Perform the target operation.

        מבצעת את פעולת היעד."""
        return self._target

    @property
    def duration(self) -> int:
        """Perform the duration operation.

        מבצעת את פעולת משך הזמן."""
        return self._duration

    @property
    def elapsed_time(self) -> int:
        """Perform the elapsed time operation.

        מבצעת את פעולת ``elapsed`` הזמן."""
        return self._elapsed_time

    @property
    def start_time(self) -> int:
        """Start time.

        מתחילה את הזמן."""
        return self._start_time

    @property
    def sequence(self) -> int:
        """Perform the sequence operation.

        מבצעת את פעולת ``sequence``."""
        return self._sequence

    @property
    def current_position(self) -> Position:
        """Perform the current position operation.

        מבצעת את פעולת ``current`` המיקום."""
        return self._path[self._current_index]

    @property
    def next_position(self) -> Position | None:
        """Perform the next position operation.

        מבצעת את פעולת ``next`` המיקום."""
        if self._current_index >= self.step_count:
            return None
        return self._path[self._current_index + 1]

    @property
    def step_count(self) -> int:
        """Perform the step count operation.

        מבצעת את פעולת ``step`` ``count``."""
        return len(self._path) - 1

    def advance_time(
        self,
        milliseconds: int,
    ) -> None:
        """Advances the motion timer.

        מקדמת את הזמן."""

        self._elapsed_time += milliseconds

    def milliseconds_until_next_step(self) -> int | None:
        """Returns the remaining time until the next cell transition.

        מבצעת את פעולת ``milliseconds`` ``until`` ``next`` ``step``."""

        if not self.is_moving():
            return None

        next_index = self._current_index + 1
        threshold = ceil((next_index * self._duration) / self.step_count)
        return max(0, threshold - self._elapsed_time)

    def is_ready_for_next_step(self) -> bool:
        """Returns whether the motion reached the next transition threshold.

        בודקת אם ``ready`` ``for`` ``next`` ``step``."""

        remaining = self.milliseconds_until_next_step()
        return remaining == 0

    def step_forward(self) -> Position:
        """Advances one board cell in the planned path.

        מבצעת את פעולת ``step`` ``forward``."""

        if self.next_position is None:
            raise ValueError("Motion already reached destination.")

        self._current_index += 1
        return self.current_position

    def stop(self) -> None:
        """Stops the motion at its current position.

        מבצעת את פעולת ``stop``."""

        self._is_stopped = True

    def is_finished(self) -> bool:
        """Returns whether the motion has completed.

        בודקת אם ``finished``."""

        return self._is_stopped or self._current_index >= self.step_count

    def is_moving(self) -> bool:
        """Returns whether the motion can still advance.

        בודקת אם ``moving``."""

        return not self._is_stopped and self._current_index < self.step_count

    def _build_path(
        self,
        piece_type: PieceType,
        source: Position,
        target: Position,
    ) -> list[Position]:
        """Builds the sequence of visited cells from source to target.

        בונה את הנתיב."""

        row_delta = target.row - source.row
        column_delta = target.column - source.column

        if piece_type == PieceType.KNIGHT:
            return [source, target]

        steps = max(abs(row_delta), abs(column_delta))

        if steps == 0:
            return [source]

        row_step = row_delta // steps
        column_step = column_delta // steps

        path = [source]

        for step_index in range(1, steps + 1):
            path.append(
                Position(
                    row=source.row + (row_step * step_index),
                    column=source.column + (column_step * step_index),
                )
            )

        return path