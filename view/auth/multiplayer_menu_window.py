"""Desktop lobby shown between authentication and an authoritative match."""

from collections.abc import Callable
import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog

from network.network_client import MultiplayerClientState, NetworkClient


class MultiplayerMenuWindow:
    """Displays the profile and sends Play/Cancel user intent to the server."""

    _POLL_INTERVAL_MS = 75

    def __init__(
        self,
        network_client: NetworkClient,
        on_match_found: Callable[[], None],
    ) -> None:
        self._client = network_client
        self._on_match_found = on_match_found
        self._root = tk.Tk()
        self._root.title("Kung Fu Chess - Multiplayer")
        self._root.resizable(False, False)
        self._status = tk.StringVar(value="Ready to play")
        self._profile = tk.StringVar()
        self._build_widgets()
        self._refresh_profile()
        self._root.after(self._POLL_INTERVAL_MS, self._poll_server)

    def run(self) -> None:
        """Run the lobby until canceled, closed, or a match is found."""
        self._root.mainloop()

    def _build_widgets(self) -> None:
        frame = ttk.Frame(self._root, padding=28)
        frame.grid()
        ttk.Label(frame, text="Kung Fu Chess", font=("Segoe UI", 18, "bold")).grid()
        ttk.Label(frame, textvariable=self._profile).grid(pady=(12, 18))
        ttk.Label(frame, textvariable=self._status).grid(pady=(0, 14))
        self._play_button = ttk.Button(frame, text="Play", command=self._play)
        self._play_button.grid(sticky="ew")
        self._create_room_button = ttk.Button(
            frame, text="Create Room", command=self._create_room
        )
        self._create_room_button.grid(pady=(8, 0), sticky="ew")
        self._join_room_button = ttk.Button(
            frame, text="Join Room", command=self._join_room
        )
        self._join_room_button.grid(pady=(8, 0), sticky="ew")
        self._spectate_button = ttk.Button(
            frame, text="Spectate Game", command=self._list_spectatable_games
        )
        self._spectate_button.grid(pady=(8, 0), sticky="ew")
        self._cancel_button = ttk.Button(
            frame,
            text="Cancel",
            command=self._cancel,
            state="disabled",
        )
        self._cancel_button.grid(pady=(8, 0), sticky="ew")

    def _play(self) -> None:
        if self._client.matchmaking_state is not MultiplayerClientState.IDLE:
            return
        self._set_entry_buttons("disabled")
        self._cancel_button.configure(state="normal")
        self._status.set("Searching for opponent...")
        self._client.start_matchmaking()

    def _cancel(self) -> None:
        if self._client.matchmaking_state is MultiplayerClientState.SEARCHING:
            self._client.cancel_matchmaking()
        elif self._client.matchmaking_state is MultiplayerClientState.ROOM_WAITING:
            self._client.cancel_room()

    def _create_room(self) -> None:
        if self._client.matchmaking_state is not MultiplayerClientState.IDLE:
            return
        self._set_entry_buttons("disabled")
        self._status.set("Creating private room...")
        self._client.create_room()

    def _join_room(self) -> None:
        if self._client.matchmaking_state is not MultiplayerClientState.IDLE:
            return
        code = simpledialog.askstring("Join Room", "Room code:", parent=self._root)
        if not code:
            return
        self._set_entry_buttons("disabled")
        self._status.set("Joining private room...")
        self._client.join_room(code)

    def _list_spectatable_games(self) -> None:
        if self._client.matchmaking_state is not MultiplayerClientState.IDLE:
            return
        self._status.set("Loading active games...")
        self._client.list_spectatable_games()

    def _poll_server(self) -> None:
        for message in self._client.poll_messages():
            message_type = message.get("type")
            if message_type == "match_found":
                self._root.destroy()
                self._on_match_found()
                return
            if message_type == "spectating_started":
                self._root.destroy()
                self._on_match_found()
                return
            if message_type == "room_created":
                code = message.get("room_code")
                self._status.set(f"Room {code}\nWaiting for another player...")
                self._cancel_button.configure(state="normal")
            elif message_type == "room_joined":
                self._status.set("Room joined. Starting match...")
            elif message_type == "room_closed":
                self._status.set("Private room closed")
                self._set_entry_buttons("normal")
                self._cancel_button.configure(state="disabled")
            elif message_type == "room_error":
                reason = str(message.get("reason", "invalid_state")).replace("_", " ")
                self._status.set(f"Room error: {reason}")
                self._set_entry_buttons("normal")
                self._cancel_button.configure(state="disabled")
            elif message_type == "spectatable_games":
                self._choose_spectatable_game(message.get("games", []))
            elif message_type == "spectator_error":
                reason = str(message.get("reason", "invalid_state")).replace("_", " ")
                self._status.set(f"Spectator error: {reason}")
            elif message_type == "matchmaking_canceled":
                self._status.set("Search canceled")
                self._set_entry_buttons("normal")
                self._cancel_button.configure(state="disabled")
            elif message_type == "matchmaking_queued":
                self._status.set("Searching for opponent...")
                self._refresh_profile()
            elif message_type in {"command_rejected", "server_error"}:
                self._status.set("Unable to start matchmaking")
                self._set_entry_buttons("normal")
                self._cancel_button.configure(state="disabled")
        self._root.after(self._POLL_INTERVAL_MS, self._poll_server)

    def _set_entry_buttons(self, state: str) -> None:
        self._play_button.configure(state=state)
        self._create_room_button.configure(state=state)
        self._join_room_button.configure(state=state)
        self._spectate_button.configure(state=state)

    def _choose_spectatable_game(self, games: object) -> None:
        if not isinstance(games, list) or not games:
            self._status.set("No active games are available")
            return
        lines = []
        for game in games:
            white = game["white"]
            black = game["black"]
            lines.append(
                f'{game["game_id"]}: {white["username"]} vs {black["username"]}'
            )
        game_id = simpledialog.askstring(
            "Spectate Game",
            "Enter a game ID:\n\n" + "\n".join(lines),
            parent=self._root,
        )
        if game_id:
            self._client.spectate_game(game_id.strip())

    def _refresh_profile(self) -> None:
        self._profile.set(f"{self._client.username}\nRating: {self._client.rating}")
