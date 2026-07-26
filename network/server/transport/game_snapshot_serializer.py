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
    """Converts public game state into a deterministic JSON-safe dictionary.

    ממיר את מצב המשחק הציבורי למילון דטרמיניסטי ובטוח ל־JSON.

    Responsibility: Converts public game state into a deterministic JSON-safe dictionary.

    אחריות: ממיר את מצב המשחק הציבורי למילון דטרמיניסטי ובטוח ל־JSON."""

    def serialize(self, game_engine: GameEngine) -> dict[str, JsonValue]:
        """Return a JSON-safe snapshot without modifying the game engine.

        מחזירה תמונת מצב בטוחה ל־JSON בלי לשנות את מנוע המשחק."""
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
        """Serialize the current board state.

        ממירה את מצב הלוח הנוכחי לייצוג סדרתי."""
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
        """Serialize one game piece.

        ממירה כלי משחק אחד לייצוג סדרתי."""
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
        """Serialize one active piece motion.

        ממירה תנועה פעילה של כלי לייצוג סדרתי."""
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
        """Serialize both players' scores.

        ממירה את תוצאות שני השחקנים לייצוג סדרתי."""
        return {
            color.name.lower(): game_engine.player_activity.get_score(color)
            for color in PieceColor
        }

    @staticmethod
    def _serialize_position(position: Position) -> dict[str, JsonValue]:
        """Serialize a board position.

        ממירה מיקום על הלוח לייצוג סדרתי."""
        return {"row": position.row, "column": position.column}

    @staticmethod
    def _serialize_color(color: PieceColor | None) -> str | None:
        """Serialize an optional piece color.

        ממירה צבע כלי אופציונלי לייצוג סדרתי."""
        if color is None:
            return None
        return color.name.lower()
