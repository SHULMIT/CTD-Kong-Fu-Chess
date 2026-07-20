"""Stores the actions and score for each player in one game."""

from dataclasses import dataclass
from datetime import datetime
from typing import Callable

from common.time import utc_now
from model.piece import PieceColor, PieceType
from model.position import Position


@dataclass(frozen=True)
class PlayerAction:
    """A player action with a timezone-aware UTC occurrence timestamp."""

    player: PieceColor
    description: str
    occurred_at: datetime


class PlayerActivityService:
    """Owns player-visible action history and capture scores."""

    _PIECE_POINTS = {
        PieceType.PAWN: 1,
        PieceType.KNIGHT: 3,
        PieceType.BISHOP: 3,
        PieceType.ROOK: 5,
        PieceType.QUEEN: 9,
        PieceType.KING: 0,
    }

    def __init__(self, clock: Callable[[], datetime] = utc_now) -> None:
        self._clock = clock
        self._actions = {
            PieceColor.WHITE: [],
            PieceColor.BLACK: [],
        }
        self._scores = {
            PieceColor.WHITE: 0,
            PieceColor.BLACK: 0,
        }

    def record_move(
        self,
        player: PieceColor,
        piece_type: PieceType,
        source: Position,
        target: Position,
    ) -> None:
        """Records a successfully scheduled move."""

        self._record_action(
            player=player,
            description=(
                f"{piece_type.name.title()} "
                f"{self._format_position(source)} -> "
                f"{self._format_position(target)}"
            ),
        )

    def record_jump(
        self,
        player: PieceColor,
        piece_type: PieceType,
        position: Position,
    ) -> None:
        """Records a jump started by a player."""

        self._record_action(
            player=player,
            description=(
                f"{piece_type.name.title()} jumps at "
                f"{self._format_position(position)}"
            ),
        )

    def record_capture(
        self,
        player: PieceColor,
        captured_piece_type: PieceType,
    ) -> None:
        """Awards points to the player who captured a piece."""

        self._scores[player] += self._PIECE_POINTS[captured_piece_type]

    def get_actions(
        self,
        player: PieceColor,
    ) -> tuple[PlayerAction, ...]:
        """Returns the player's actions in execution order."""

        return tuple(self._actions[player])

    def get_score(
        self,
        player: PieceColor,
    ) -> int:
        """Returns the player's accumulated capture score."""

        return self._scores[player]

    def _record_action(
        self,
        player: PieceColor,
        description: str,
    ) -> None:
        history = self._actions[player]
        history.append(
            PlayerAction(
                player=player,
                description=description,
                occurred_at=self._clock(),
            )
        )

    @staticmethod
    def _format_position(position: Position) -> str:
        return f"{chr(ord('A') + position.column)}{8 - position.row}"
