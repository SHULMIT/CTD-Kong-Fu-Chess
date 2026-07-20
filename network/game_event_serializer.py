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
from network.game_snapshot_serializer import JsonValue


class GameEventSerializer:
    """Converts supported domain events into explicit network payloads."""

    def serialize(self, event: Event) -> dict[str, JsonValue]:
        """Return a JSON-safe payload for a server-observed game event."""
        if isinstance(event, MoveStartedEvent):
            return self._serialize_move("move_started", event)
        if isinstance(event, MoveCompletedEvent):
            return self._serialize_move("move_completed", event)
        if isinstance(event, JumpStartedEvent):
            return self._serialize_jump("jump_started", event)
        if isinstance(event, JumpCompletedEvent):
            return self._serialize_jump("jump_completed", event)
        if isinstance(event, ScoreChangedEvent):
            return {
                "type": "score_changed",
                "player": event.player.name.lower(),
                "score": event.score,
            }
        if isinstance(event, GameOverEvent):
            winner = None
            if event.winner is not None:
                winner = event.winner.name.lower()
            return {"type": "game_over", "winner": winner}
        raise ValueError(f"Unsupported game event: {type(event).__name__}")

    @staticmethod
    def _serialize_move(
        event_type: str,
        event: MoveStartedEvent | MoveCompletedEvent,
    ) -> dict[str, JsonValue]:
        return {
            "type": event_type,
            "piece_id": event.piece_id,
            "source": GameEventSerializer._position(event.source),
            "target": GameEventSerializer._position(event.target),
        }

    @staticmethod
    def _serialize_jump(
        event_type: str,
        event: JumpStartedEvent | JumpCompletedEvent,
    ) -> dict[str, JsonValue]:
        return {
            "type": event_type,
            "piece_id": event.piece_id,
            "position": GameEventSerializer._position(event.position),
        }

    @staticmethod
    def _position(position: Position) -> dict[str, JsonValue]:
        return {"row": position.row, "column": position.column}
