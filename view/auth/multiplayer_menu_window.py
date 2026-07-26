"""Desktop lobby shown between authentication and an authoritative match."""

from collections.abc import Callable
import tkinter as tk
from tkinter import ttk

from network.network_client import MultiplayerClientState, NetworkClient
from view.auth.text_prompt import ask_text
from view.auth.ui_theme import apply_desktop_theme, fit_and_center


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
        apply_desktop_theme(self._root)
        self._status = tk.StringVar(value="●  Ready to play")
        self._profile = tk.StringVar()
        self._build_widgets()
        fit_and_center(self._root, 460)
        self._refresh_profile()
        self._root.after(self._POLL_INTERVAL_MS, self._poll_server)

    def run(self) -> None:
        """Run the lobby until canceled, closed, or a match is found."""
        self._root.mainloop()

    def _build_widgets(self) -> None:
        outer = ttk.Frame(self._root, style="App.TFrame", padding=18)
        outer.grid(sticky="nsew")
        frame = ttk.Frame(outer, style="Card.TFrame", padding=32)
        frame.grid(sticky="nsew")
        frame.columnconfigure((0, 1), weight=1, uniform="menu")
        ttk.Label(frame, text="Kung Fu Chess", style="Title.TLabel").grid(
            row=0, column=0, columnspan=2
        )
        ttk.Label(
            frame, text="MULTIPLAYER LOBBY", style="Subtitle.TLabel"
        ).grid(row=1, column=0, columnspan=2, pady=(4, 18))
        ttk.Label(
            frame,
            textvariable=self._profile,
            style="Body.TLabel",
            anchor="center",
            justify="center",
        ).grid(row=2, column=0, columnspan=2, sticky="ew")
        self._status_label = ttk.Label(
            frame,
            textvariable=self._status,
            style="Info.TLabel",
            anchor="center",
            justify="center",
            wraplength=360,
        )
        self._status_label.grid(
            row=3, column=0, columnspan=2, pady=(16, 20), sticky="ew"
        )
        self._play_button = ttk.Button(
            frame, text="Find Match", style="Primary.TButton", command=self._play
        )
        self._play_button.grid(row=4, column=0, columnspan=2, sticky="ew")
        self._create_room_button = ttk.Button(
            frame,
            text="Create Room",
            style="Secondary.TButton",
            command=self._create_room,
        )
        self._create_room_button.grid(
            row=5,
            column=0,
            pady=(10, 0),
            padx=(0, 5),
            sticky="ew",
        )
        self._join_room_button = ttk.Button(
            frame,
            text="Join Room",
            style="Secondary.TButton",
            command=self._join_room,
        )
        self._join_room_button.grid(
            row=5,
            column=1,
            pady=(10, 0),
            padx=(5, 0),
            sticky="ew",
        )
        self._spectate_button = ttk.Button(
            frame,
            text="Spectate Game",
            style="Secondary.TButton",
            command=self._list_spectatable_games,
        )
        self._spectate_button.grid(
            row=6, column=0, columnspan=2, pady=(10, 0), sticky="ew"
        )
        self._cancel_button = ttk.Button(
            frame,
            text="Cancel",
            style="Danger.TButton",
            command=self._cancel,
            state="disabled",
        )
        self._cancel_button.grid(row=7, column=0, columnspan=2, pady=(10, 0), sticky="ew")

    def _play(self) -> None:
        if self._client.matchmaking_state is not MultiplayerClientState.IDLE:
            return
        self._set_entry_buttons("disabled")
        self._cancel_button.configure(state="normal")
        self._set_status("Searching for opponent...")
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
        self._set_status("Creating private room...")
        self._client.create_room()

    def _join_room(self) -> None:
        if self._client.matchmaking_state is not MultiplayerClientState.IDLE:
            return
        code = ask_text(self._root, "Join Room", "Enter the private room code.")
        if not code:
            return
        self._set_entry_buttons("disabled")
        self._set_status("Joining private room...")
        self._client.join_room(code)

    def _list_spectatable_games(self) -> None:
        if self._client.matchmaking_state is not MultiplayerClientState.IDLE:
            return
        self._set_status("Loading active games...")
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
                self._set_status(
                    f"Room {code}\nWaiting for another player...",
                    "success",
                )
                self._cancel_button.configure(state="normal")
            elif message_type == "room_joined":
                self._set_status("Room joined. Starting match...", "success")
            elif message_type == "room_closed":
                self._set_status("Private room closed")
                self._set_entry_buttons("normal")
                self._cancel_button.configure(state="disabled")
            elif message_type == "room_error":
                reason = str(message.get("reason", "invalid_state")).replace("_", " ")
                self._set_status(f"Room error: {reason}", "error")
                self._set_entry_buttons("normal")
                self._cancel_button.configure(state="disabled")
            elif message_type == "spectatable_games":
                self._choose_spectatable_game(message.get("games", []))
            elif message_type == "spectator_error":
                reason = str(message.get("reason", "invalid_state")).replace("_", " ")
                self._set_status(f"Spectator error: {reason}", "error")
            elif message_type == "matchmaking_canceled":
                self._set_status("Search canceled")
                self._set_entry_buttons("normal")
                self._cancel_button.configure(state="disabled")
            elif message_type == "matchmaking_queued":
                self._set_status("Searching for opponent...")
                self._refresh_profile()
            elif message_type in {"command_rejected", "server_error"}:
                self._set_status("Unable to start matchmaking", "error")
                self._set_entry_buttons("normal")
                self._cancel_button.configure(state="disabled")
        self._root.after(self._POLL_INTERVAL_MS, self._poll_server)

    def _set_entry_buttons(self, state: str) -> None:
        self._play_button.configure(state=state)
        self._create_room_button.configure(state=state)
        self._join_room_button.configure(state=state)
        self._spectate_button.configure(state=state)

    def _set_status(self, message: str, tone: str = "info") -> None:
        """Present lobby feedback with a consistent semantic treatment."""
        styles = {
            "info": ("Info.TLabel", "●"),
            "success": ("Success.TLabel", "✓"),
            "error": ("Error.TLabel", "!"),
        }
        style, icon = styles.get(tone, styles["info"])
        self._status.set(f"{icon}  {message}")
        self._status_label.configure(style=style)

    def _choose_spectatable_game(self, games: object) -> None:
        if not isinstance(games, list) or not games:
            self._set_status("No active games are available")
            return
        lines = []
        for game in games:
            white = game["white"]
            black = game["black"]
            lines.append(
                f'{game["game_id"]}: {white["username"]} vs {black["username"]}'
            )
        game_id = ask_text(
            self._root,
            "Spectate Game",
            "Choose an active game by ID:\n\n" + "\n".join(lines),
        )
        if game_id:
            self._client.spectate_game(game_id.strip())

    def _refresh_profile(self) -> None:
        self._profile.set(f"{self._client.username}\nRating: {self._client.rating}")
