"""UI command adapter for a server-authoritative multiplayer game."""

from errors.user_input_errors import ClickEmptySourceError, ClickOutsideBoardError
from model.position import Position
from network.network_client import NetworkClient
from network.remote_game_state import RemoteGameState


class MultiplayerController:
    """Translates board input into network commands without local game rules."""

    def __init__(
        self,
        game_state: RemoteGameState,
        network_client: NetworkClient,
    ) -> None:
        self._game_state = game_state
        self._network_client = network_client
        self._selected_position: Position | None = None
        self._selected_piece_id: int | None = None

    @property
    def selected_position(self) -> Position | None:
        self._clear_invalid_selection()
        return self._selected_position

    def handle_position(self, position: Position) -> None:
        """Select a source or send a move request to the server."""
        if not self._game_state.is_inside(position):
            self._clear_selection()
            raise ClickOutsideBoardError()

        if self._selected_position is None:
            if not self._game_state.has_piece(position):
                raise ClickEmptySourceError()
            piece = self._game_state.get_piece(position)
            self._selected_position = position
            self._selected_piece_id = piece.id if piece is not None else None
            self._game_state.clear_legal_moves()
            self._network_client.request_legal_moves(position)
            return

        selected_piece = self._game_state.get_piece(self._selected_position)
        target_piece = self._game_state.get_piece(position)
        if (
            selected_piece is not None
            and target_piece is not None
            and selected_piece.color is target_piece.color
        ):
            self._selected_position = position
            self._selected_piece_id = target_piece.id
            self._game_state.clear_legal_moves()
            self._network_client.request_legal_moves(position)
            return

        source = self._selected_position
        self._clear_selection()
        self._network_client.send_move(source, position)

    def jump_at(self, position: Position) -> None:
        """Send a jump request without applying it locally."""
        self._network_client.send_jump(position)

    def deselect(self) -> None:
        """Clear the current local selection."""
        self._clear_selection()

    def _clear_invalid_selection(self) -> None:
        selected = self._selected_position
        if selected is None:
            return
        piece = self._game_state.get_piece(selected)
        assigned_color = self._network_client.assigned_color
        if (
            piece is not None
            and piece.id == self._selected_piece_id
            and piece.color is assigned_color
        ):
            return
        self._clear_selection()

    def _clear_selection(self) -> None:
        self._selected_position = None
        self._selected_piece_id = None
        self._game_state.clear_legal_moves()
