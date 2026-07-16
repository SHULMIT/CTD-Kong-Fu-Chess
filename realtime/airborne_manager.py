"""
Tracks and resolves airborne piece timers.
"""

from model.piece import Piece, PieceState


class AirborneManager:
    """
    Owns the airborne timer state.

    This service has a single responsibility:
    manage jump timers.
    """

    def __init__(
        self,
        jump_duration_milliseconds: int,
    ):
        self._jump_duration_milliseconds = jump_duration_milliseconds
        self._airborne_timers: dict[Piece, int] = {}

    def has_airborne_pieces(self) -> bool:
        """
        Returns whether there are active airborne timers.
        """

        return len(self._airborne_timers) > 0

    def jump(
        self,
        piece: Piece,
    ) -> None:
        """
        Starts (or refreshes) airborne state for a piece.
        """

        piece.state = PieceState.AIRBORNE
        self._airborne_timers[piece] = self._jump_duration_milliseconds

    def advance_time(
        self,
        milliseconds: int,
    ) -> None:
        """
        Advances all airborne timers by the same time slice.
        """

        for piece in list(self._airborne_timers):
            self._airborne_timers[piece] -= milliseconds

    def time_until_next_landing(self) -> int | None:
        """
        Returns the shortest remaining timer among airborne pieces.
        """

        if not self._airborne_timers:
            return None

        return min(self._airborne_timers.values())

    def consume_finished_landings(
        self,
    ) -> list[Piece]:
        """
        Returns and removes pieces whose airborne timers completed.
        """

        landed = []

        for piece, remaining in list(
            self._airborne_timers.items()
        ):

            if remaining > 0:
                continue

            landed.append(piece)

            self._airborne_timers.pop(piece)

        return landed

    def remove_piece(
        self,
        piece: Piece,
    ) -> None:
        """
        Removes a piece from airborne tracking.
        """

        self._airborne_timers.pop(piece, None)
