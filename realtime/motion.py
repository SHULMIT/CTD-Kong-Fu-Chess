"""
Represents a single active piece movement.
"""

from model.piece import Piece
from model.position import Position


class Motion:
    """
    Represents a single active movement.
    """

    def __init__(
        self,
        piece: Piece,
        source: Position,
        target: Position,
        duration: int,
    ):
        self._piece = piece
        self._source = source
        self._target = target
        self._duration = duration
        self._elapsed_time = 0

    @property
    def piece(self) -> Piece:
        return self._piece

    @property
    def source(self) -> Position:
        return self._source

    @property
    def target(self) -> Position:
        return self._target

    @property
    def duration(self) -> int:
        return self._duration

    @property
    def elapsed_time(self) -> int:
        return self._elapsed_time

    def advance_time(
        self,
        milliseconds: int,
    ) -> None:
        """
        Advances the motion timer.
        """

        self._elapsed_time += milliseconds

    def is_finished(self) -> bool:
        """
        Returns whether the motion has completed.
        """

        return self._elapsed_time >= self._duration