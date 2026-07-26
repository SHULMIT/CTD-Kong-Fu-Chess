"""Lobby and spectating commands for an authenticated multiplayer client."""

from __future__ import annotations

from concurrent.futures import Future

from network.authentication_client import MessageSender
from network.client_session_state import ClientSessionState, MultiplayerClientState


class MatchmakingClient:
    """Validate local lobby state before sending lobby commands."""

    def __init__(self, transport: MessageSender, session: ClientSessionState) -> None:
        self._transport = transport
        self._session = session

    def start_matchmaking(self) -> Future[None]:
        """Enter matchmaking from the idle state."""
        if self._session.matchmaking_state is not MultiplayerClientState.IDLE:
            raise RuntimeError("The client is already matchmaking or in a game.")
        self._session.set_matchmaking_state(MultiplayerClientState.SEARCHING)
        try:
            return self._transport.send({"type": "start_matchmaking"})
        except Exception:
            self._session.set_matchmaking_state(MultiplayerClientState.IDLE)
            raise

    def cancel_matchmaking(self) -> Future[None]: return self._transport.send({"type": "cancel_matchmaking"})
    def create_room(self) -> Future[None]: return self._send_when_idle({"type": "create_room"})
    def join_room(self, room_code: str) -> Future[None]: return self._send_when_idle({"type": "join_room", "room_code": room_code})
    def cancel_room(self) -> Future[None]: return self._transport.send({"type": "cancel_room"})
    def list_spectatable_games(self) -> Future[None]: return self._transport.send({"type": "list_spectatable_games"})
    def spectate_game(self, game_id: str) -> Future[None]: return self._transport.send({"type": "spectate_game", "game_id": game_id})
    def stop_spectating(self) -> Future[None]: return self._transport.send({"type": "stop_spectating"})

    def _send_when_idle(self, message: dict[str, object]) -> Future[None]:
        if self._session.matchmaking_state is not MultiplayerClientState.IDLE:
            raise RuntimeError("The client is not idle.")
        return self._transport.send(message)
