"""JSON-safe serialization for domain events sent to remote clients."""

from events.event import Event
from events.game_events import (
    GameOverEvent,
    JumpCompletedEvent,
    JumpStartedEvent,
    MoveCompletedEvent,
    MoveStartedEvent,
    ScoreChangedEvent,
)
from model.position import Position
from network.game_event_type import GameEventType
from network.server.transport.game_snapshot_serializer import JsonValue


class GameEventSerializer:
    """Converts supported domain events into explicit network payloads.

    ממיר אירועי תחום נתמכים למטעני רשת מפורשים.

    Responsibility: Converts supported domain events into explicit network payloads.

    אחריות: ממיר אירועי תחום נתמכים למטעני רשת מפורשים."""

    def serialize(self, event: Event) -> dict[str, JsonValue]:
        """Return a JSON-safe payload for a server-observed game event.

        מחזירה מטען בטוח ל־JSON עבור אירוע משחק שנצפה בשרת."""
        if isinstance(event, MoveStartedEvent):
            return self._serialize_move(GameEventType.MOVE_STARTED, event)
        if isinstance(event, MoveCompletedEvent):
            return self._serialize_move(GameEventType.MOVE_COMPLETED, event)
        if isinstance(event, JumpStartedEvent):
            return self._serialize_jump(GameEventType.JUMP_STARTED, event)
        if isinstance(event, JumpCompletedEvent):
            return self._serialize_jump(GameEventType.JUMP_COMPLETED, event)
        if isinstance(event, ScoreChangedEvent):
            return {
                "type": GameEventType.SCORE_CHANGED.value,
                "player": event.player.name.lower(),
                "score": event.score,
            }
        if isinstance(event, GameOverEvent):
            winner = None
            if event.winner is not None:
                winner = event.winner.name.lower()
            return {"type": GameEventType.GAME_OVER.value, "winner": winner}
        raise ValueError(f"Unsupported game event: {type(event).__name__}")

    @staticmethod
    def _serialize_move(
        event_type: GameEventType,
        event: MoveStartedEvent | MoveCompletedEvent,
    ) -> dict[str, JsonValue]:
        """Serialize a move event for transport.

        ממירה אירוע תנועה לייצוג המיועד לתעבורה."""
        return {
            "type": event_type.value,
            "piece_id": event.piece_id,
            "source": GameEventSerializer._position(event.source),
            "target": GameEventSerializer._position(event.target),
        }

    @staticmethod
    def _serialize_jump(
        event_type: GameEventType,
        event: JumpStartedEvent | JumpCompletedEvent,
    ) -> dict[str, JsonValue]:
        """Serialize a jump event for transport.

        ממירה אירוע קפיצה לייצוג המיועד לתעבורה."""
        return {
            "type": event_type.value,
            "piece_id": event.piece_id,
            "position": GameEventSerializer._position(event.position),
        }

    @staticmethod
    def _position(position: Position) -> dict[str, JsonValue]:
        """Serialize a board position for transport.

        ממירה מיקום על הלוח לייצוג המיועד לתעבורה."""
        return {"row": position.row, "column": position.column}
