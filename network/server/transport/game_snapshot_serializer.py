"""JSON-safe serialization of the current public game state."""

from typing import TypeAlias

from game.game_engine import GameEngine
from model.board import Board
from model.piece import Piece, PieceColor
from model.position import Position
from realtime.motion import Motion

JsonValue: TypeAlias = (
    dict[str, "JsonValue"]
    | list["JsonValue"]
    | str
    | int
    | float
    | bool
    | None
)


class GameSnapshotSerializer:
    """Converts public game state into a deterministic JSON-safe dictionary."""

    def serialize(self, game_engine: GameEngine) -> dict[str, JsonValue]:
        """Return a JSON-safe snapshot without modifying the game engine."""
        board = game_engine.get_board()
        winner = game_engine.get_winner()
        return {
            "board": self._serialize_board(board),
            "motions": [
                self._serialize_motion(motion)
                for motion in game_engine.get_motions()
            ],
            "scores": self._serialize_scores(game_engine),
            "game_over": game_engine.game_over,
            "winner": self._serialize_color(winner),
        }

    def _serialize_board(self, board: Board) -> dict[str, JsonValue]:
        pieces: list[JsonValue] = []
        for row in range(board.height):
            for column in range(board.width):
                piece = board.get_piece(Position(row, column))
                if isinstance(piece, Piece):
                    pieces.append(self._serialize_piece(piece))
        return {
            "width": board.width,
            "height": board.height,
            "pieces": pieces,
        }

    @staticmethod
    def _serialize_piece(piece: Piece) -> dict[str, JsonValue]:
        return {
            "id": piece.id,
            "type": piece.type.name.lower(),
            "color": piece.color.name.lower(),
            "state": piece.state.name.lower(),
            "position": GameSnapshotSerializer._serialize_position(
                piece.position
            ),
        }

    @staticmethod
    def _serialize_motion(motion: Motion) -> dict[str, JsonValue]:
        return {
            "piece_id": motion.piece.id,
            "source": GameSnapshotSerializer._serialize_position(
                motion.source
            ),
            "target": GameSnapshotSerializer._serialize_position(
                motion.target
            ),
            "current_position": GameSnapshotSerializer._serialize_position(
                motion.current_position
            ),
            "duration": motion.duration,
            "elapsed_time": motion.elapsed_time,
        }

    @staticmethod
    def _serialize_scores(
        game_engine: GameEngine,
    ) -> dict[str, JsonValue]:
        return {
            color.name.lower(): game_engine.player_activity.get_score(color)
            for color in PieceColor
        }

    @staticmethod
    def _serialize_position(position: Position) -> dict[str, JsonValue]:
        return {"row": position.row, "column": position.column}

    @staticmethod
    def _serialize_color(color: PieceColor | None) -> str | None:
        if color is None:
            return None
        return color.name.lower()
