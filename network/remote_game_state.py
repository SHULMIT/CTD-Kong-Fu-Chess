"""Read-only UI state reconstructed from authoritative server snapshots."""

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from typing import Any

from common.time import utc_now
from config.constants import EMPTY_SQUARE
from game.player_activity_service import PlayerAction
from model.board import Board
from model.piece import Piece, PieceColor, PieceState, PieceType
from model.position import Position
from network.game_event_type import GameEventType
from network.network_client import NetworkClient


class RemotePlayerActivity:
    """Provides snapshot scores through the existing renderer-facing API."""

    def __init__(self) -> None:
        self._scores = {color: 0 for color in PieceColor}
        self._actions: dict[PieceColor, list[PlayerAction]] = {
            color: [] for color in PieceColor
        }
        self._profiles: dict[PieceColor, tuple[str, int, bool]] = {}

    def update_scores(self, scores: dict[str, object]) -> None:
        """Replace displayed scores with authoritative snapshot values."""
        for color in PieceColor:
            score = scores.get(color.name.lower())
            if type(score) is int:
                self._scores[color] = score

    def get_score(self, player: PieceColor) -> int:
        """Return the latest authoritative score for a player."""
        return self._scores[player]

    def get_actions(self, player: PieceColor) -> tuple[PlayerAction, ...]:
        """Return an immutable snapshot of server-derived activity."""
        return tuple(self._actions[player])

    def record_action(self, player: PieceColor, description: str) -> None:
        """Append one presentation-only action derived from a game event."""
        self._actions[player].append(
            PlayerAction(
                player=player,
                description=description,
                occurred_at=utc_now(),
            )
        )

    def set_profile(
        self,
        color: PieceColor,
        username: str,
        rating: int,
        is_local: bool = False,
    ) -> None:
        """Set the authenticated profile displayed for the local color."""
        self._profiles[color] = (username, rating, is_local)

    def get_profile(self, color: PieceColor) -> tuple[str, int, bool] | None:
        """Return display profile data for a color, if known."""
        return self._profiles.get(color)


@dataclass(frozen=True)
class RemoteMotion:
    """Rendering data for one active motion from a server snapshot."""

    piece: Piece
    source: Position
    target: Position
    current_position: Position
    duration: int
    elapsed_time: int


class RemoteGameState:
    """Applies server snapshots without running authoritative game logic."""

    def __init__(self, network_client: NetworkClient) -> None:
        self._network_client = network_client
        self._board = Board([])
        self._pieces_by_id: dict[int, Piece] = {}
        self._motions: tuple[RemoteMotion, ...] = ()
        self._player_activity = RemotePlayerActivity()
        self._game_over = False
        self._winner: PieceColor | None = None
        self._last_event: dict[str, Any] | None = None
        self._last_response: dict[str, Any] | None = None
        self._legal_moves_source: Position | None = None
        self._legal_moves: set[Position] = set()
        self._seen_event_keys: set[tuple[str, object]] = set()
        self._pending_match_started_message: str | None = None
        self._match_started_received = False
        self._disconnect_username: str | None = None
        self._disconnect_deadline: datetime | None = None
        self._disconnect_notice: str | None = None
        self._spectator_view_closed = False

    @property
    def board(self) -> Board:
        """Return the latest board reconstructed on the UI thread."""
        return self._board

    @property
    def player_activity(self) -> RemotePlayerActivity:
        """Return renderer-facing authoritative score data."""
        return self._player_activity

    @property
    def game_over(self) -> bool:
        """Return the latest authoritative terminal-state flag."""
        return self._game_over

    @property
    def last_event(self) -> dict[str, Any] | None:
        """Return the most recently received game-event message."""
        return self._last_event

    @property
    def last_response(self) -> dict[str, Any] | None:
        """Return the latest command or server response."""
        return self._last_response

    def wait(self, _milliseconds: int) -> None:
        """Apply queued server messages; never advance a local simulation."""
        for message in self._network_client.poll_messages():
            self.apply_message(message)

    def apply_message(self, message: dict[str, Any]) -> None:
        """Apply one server message on the calling UI thread."""
        message_type = message.get("type")
        if message_type == "game_snapshot":
            state = message.get("state")
            if isinstance(state, dict):
                self._apply_snapshot(state)
        elif message_type == "game_event":
            self._apply_game_event(message)
        elif message_type == "legal_moves":
            self._apply_legal_moves(message)
        elif message_type in {"match_found", "player_profiles", "rating_updated"}:
            self._apply_player_profiles(
                message,
                show_match_dialog=message_type in {"match_found", "player_profiles"},
            )
        elif message_type in {
            "command_accepted",
            "command_rejected",
            "server_error",
        }:
            self._last_response = message
        elif message_type == "opponent_disconnected":
            self.clear_legal_moves()
            self._disconnect_username = str(message.get("username", "Opponent"))
            try:
                self._disconnect_deadline = datetime.fromisoformat(str(message["deadline"]))
            except (KeyError, ValueError):
                self._disconnect_deadline = None
            self._disconnect_notice = None
        elif message_type == "opponent_reconnected":
            self._disconnect_username = None
            self._disconnect_deadline = None
            self._disconnect_notice = "Opponent reconnected"
        elif message_type == "connection_lost":
            self.clear_legal_moves()
            self._disconnect_notice = "Connection lost - reconnecting..."
        elif message_type == "session_resumed":
            self.clear_legal_moves()
            self._disconnect_notice = None
        elif message_type == "disconnect_forfeit":
            self.clear_legal_moves()
            self._disconnect_username = None
            self._disconnect_deadline = None
            winner = message.get("winner")
            self._disconnect_notice = (
                f"{winner} wins by disconnect forfeit" if winner else "Game ended"
            )
        elif message_type == "spectating_stopped":
            self._spectator_view_closed = True

    def should_close_spectator_view(self) -> bool:
        """Return whether the server ended this spectator view."""
        return self._spectator_view_closed

    def disconnect_overlay_message(self) -> str | None:
        """Return current presentation text using the server deadline."""
        if self._disconnect_username is None:
            return self._disconnect_notice
        remaining = 0
        if self._disconnect_deadline is not None:
            remaining = max(
                0,
                int((self._disconnect_deadline - datetime.now(timezone.utc)).total_seconds()) + 1,
            )
        return (
            f"Opponent disconnected\nWaiting for {self._disconnect_username} "
            f"to reconnect...\n{remaining} seconds remaining"
        )

    def is_inside(self, position: Position) -> bool:
        return self._board.is_inside(position)

    def has_piece(self, position: Position) -> bool:
        if not self.is_inside(position):
            return False
        return isinstance(self._board.get_piece(position), Piece)

    def get_piece(self, position: Position) -> Piece | None:
        if not self.is_inside(position):
            return None
        piece = self._board.get_piece(position)
        return piece if isinstance(piece, Piece) else None

    def get_motions(self) -> tuple[RemoteMotion, ...]:
        return self._motions

    def get_legal_moves(self, source: Position) -> set[Position]:
        """Return destinations supplied by the server for this source."""
        if source != self._legal_moves_source:
            return set()
        return set(self._legal_moves)

    def clear_legal_moves(self) -> None:
        """Clear destination markers after selection state changes."""
        self._legal_moves_source = None
        self._legal_moves.clear()

    def set_local_profile(
        self,
        color: PieceColor | None,
        username: str | None,
        rating: int | None,
    ) -> None:
        """Attach the authenticated identity to its assigned color panel."""
        if color is None or username is None or rating is None:
            return
        self._player_activity.set_profile(color, username, rating, is_local=True)

    def consume_match_started_message(self) -> str | None:
        """Return the pending match dialog text exactly once."""
        message = self._pending_match_started_message
        self._pending_match_started_message = None
        return message

    def get_winner(self) -> PieceColor | None:
        return self._winner

    def get_board(self) -> Board:
        return self._board

    def _apply_snapshot(self, snapshot: dict[str, Any]) -> None:
        board_data = snapshot["board"]
        width = board_data["width"]
        height = board_data["height"]
        rows = [[EMPTY_SQUARE for _ in range(width)] for _ in range(height)]

        for piece_data in board_data["pieces"]:
            piece = self._piece_from_data(piece_data)
            rows[piece.position.row][piece.position.column] = piece

        self._board = Board(rows)
        self._motions = tuple(
            self._motion_from_data(motion_data)
            for motion_data in snapshot["motions"]
        )
        self._player_activity.update_scores(snapshot["scores"])
        self._game_over = bool(snapshot["game_over"])
        winner = snapshot["winner"]
        self._winner = (
            PieceColor[str(winner).upper()]
            if winner is not None
            else None
        )
        self._clear_legal_moves_if_source_changed()

    def _apply_legal_moves(self, message: dict[str, Any]) -> None:
        source = self._position(message["source"])
        positions = {
            self._position(position)
            for position in message["positions"]
        }
        self._legal_moves_source = source
        self._legal_moves = positions

    def _apply_player_profiles(
        self,
        message: dict[str, Any],
        show_match_dialog: bool,
    ) -> None:
        lines = []
        for profile in message.get("players", []):
            color = PieceColor[str(profile["color"]).upper()]
            username = str(profile["username"])
            rating = int(profile["rating"])
            self._player_activity.set_profile(
                color,
                username,
                rating,
                is_local=color is self._network_client.assigned_color,
            )
            lines.append(f"{color.name.title()}: {username} ({rating})")
        if (
            show_match_dialog
            and len(lines) == 2
            and not self._match_started_received
        ):
            self._match_started_received = True
            self._pending_match_started_message = "\n".join(lines)

    def _apply_game_event(self, message: dict[str, Any]) -> None:
        event_key = self._event_key(message)
        if event_key in self._seen_event_keys:
            return
        self._seen_event_keys.add(event_key)
        self._last_event = message
        event = message.get("event")
        if not isinstance(event, dict):
            return

        event_type = event.get("type")
        try:
            if event_type == GameEventType.MOVE_STARTED:
                self._record_move_event(event)
            elif event_type == GameEventType.JUMP_STARTED:
                self._record_jump_event(event)
            elif event_type == GameEventType.SCORE_CHANGED:
                self._record_score_event(event)
            elif event_type == GameEventType.GAME_OVER:
                self._record_game_over_event(event)
        except (KeyError, TypeError, ValueError):
            return

    def _record_move_event(self, event: dict[str, Any]) -> None:
        piece = self._pieces_by_id.get(int(event["piece_id"]))
        if piece is None:
            return
        source = self._position(event["source"])
        target = self._position(event["target"])
        self._player_activity.record_action(
            piece.color,
            (
                f"{piece.type.name.title()} "
                f"{self._format_position(source)} -> "
                f"{self._format_position(target)}"
            ),
        )

    def _record_jump_event(self, event: dict[str, Any]) -> None:
        piece = self._pieces_by_id.get(int(event["piece_id"]))
        if piece is None:
            return
        position = self._position(event["position"])
        self._player_activity.record_action(
            piece.color,
            (
                f"{piece.type.name.title()} jumps at "
                f"{self._format_position(position)}"
            ),
        )

    def _record_score_event(self, event: dict[str, Any]) -> None:
        player = PieceColor[str(event["player"]).upper()]
        score = int(event["score"])
        self._player_activity.update_scores({player.name.lower(): score})
        self._player_activity.record_action(
            player,
            f"Capture - score: {score}",
        )

    def _record_game_over_event(self, event: dict[str, Any]) -> None:
        winner_value = event.get("winner")
        if winner_value is None:
            for player in PieceColor:
                self._player_activity.record_action(player, "Game over")
            return
        winner = PieceColor[str(winner_value).upper()]
        self._player_activity.record_action(
            winner,
            f"Game over - {winner.name.title()} wins",
        )

    def _clear_legal_moves_if_source_changed(self) -> None:
        source = self._legal_moves_source
        if source is None:
            return
        if (
            not self._board.is_inside(source)
            or not isinstance(self._board.get_piece(source), Piece)
        ):
            self.clear_legal_moves()

    @staticmethod
    def _event_key(message: dict[str, Any]) -> tuple[str, object]:
        event_id = message.get("event_id")
        if type(event_id) is int:
            return ("id", event_id)
        return ("payload", json.dumps(message.get("event"), sort_keys=True))

    @staticmethod
    def _format_position(position: Position) -> str:
        return f"{chr(ord('A') + position.column)}{8 - position.row}"

    def _piece_from_data(self, data: dict[str, Any]) -> Piece:
        piece_id = int(data["id"])
        position = self._position(data["position"])
        piece = self._pieces_by_id.get(piece_id)
        if piece is None:
            piece = Piece(
                piece_id=piece_id,
                piece_type=PieceType[str(data["type"]).upper()],
                color=PieceColor[str(data["color"]).upper()],
                position=position,
            )
            self._pieces_by_id[piece_id] = piece
        piece.type = PieceType[str(data["type"]).upper()]
        piece.position = position
        piece.state = PieceState[str(data["state"]).upper()]
        return piece

    def _motion_from_data(self, data: dict[str, Any]) -> RemoteMotion:
        piece = self._pieces_by_id[int(data["piece_id"])]
        return RemoteMotion(
            piece=piece,
            source=self._position(data["source"]),
            target=self._position(data["target"]),
            current_position=self._position(data["current_position"]),
            duration=int(data["duration"]),
            elapsed_time=int(data["elapsed_time"]),
        )

    @staticmethod
    def _position(data: dict[str, Any]) -> Position:
        return Position(row=int(data["row"]), column=int(data["column"]))
