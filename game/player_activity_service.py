"""Stores the actions and score for each player in one game."""

from dataclasses import dataclass

from model.piece import PieceColor, PieceType
from model.position import Position


@dataclass(frozen=True)
class PlayerAction:
    """A single player action, timestamped on the simulation clock."""

    player: PieceColor
    description: str
    timestamp_milliseconds: int


class PlayerActivityService:
    """Owns player-visible action history and capture scores."""

    MAX_PLAYER_ACTIONS = 8

    _PIECE_POINTS = {
        PieceType.PAWN: 1,
        PieceType.KNIGHT: 3,
        PieceType.BISHOP: 3,
        PieceType.ROOK: 5,
        PieceType.QUEEN: 9,
        PieceType.KING: 0,
    }

    def __init__(self) -> None:
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
        timestamp_milliseconds: int,
    ) -> None:
        """Records a successfully scheduled move."""

        self._record_action(
            player=player,
            description=(
                f"{piece_type.name.title()} "
                f"{self._format_position(source)} -> "
                f"{self._format_position(target)}"
            ),
            timestamp_milliseconds=timestamp_milliseconds,
        )

    def record_jump(
        self,
        player: PieceColor,
        piece_type: PieceType,
        position: Position,
        timestamp_milliseconds: int,
    ) -> None:
        """Records a jump started by a player."""

        self._record_action(
            player=player,
            description=(
                f"{piece_type.name.title()} jumps at "
                f"{self._format_position(position)}"
            ),
            timestamp_milliseconds=timestamp_milliseconds,
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
        timestamp_milliseconds: int,
    ) -> None:
        history = self._actions[player]
        history.append(
            PlayerAction(
                player=player,
                description=description,
                timestamp_milliseconds=timestamp_milliseconds,
            )
        )
        # Keep the history bounded to the maximum number of actions.
        if len(history) > self.MAX_PLAYER_ACTIONS:
            history.pop(0)

    @staticmethod
    def _format_position(position: Position) -> str:
        return f"{chr(ord('A') + position.column)}{8 - position.row}"
