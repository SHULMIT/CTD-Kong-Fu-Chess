"""Tk desktop login and registration window for multiplayer mode."""

from collections.abc import Callable
import queue
import threading
import tkinter as tk
from tkinter import ttk
from typing import Any

from view.auth.ui_theme import apply_desktop_theme, fit_and_center


class LoginWindow:
    """Collects credentials and displays safe structured auth responses."""

    _MESSAGES = {
        "registration_success": "Registration succeeded. You can now log in.",
        "username_taken": (
            "An account with this username already exists. "
            "Log in with its password or choose another username."
        ),
        "invalid_credentials": "Invalid username or password.",
        "validation_error": (
            "Username: 3-32 letters, numbers or _. Password: 8-128 characters."
        ),
        "server_error": "The server encountered an error. Please try again.",
        "connection_rejected": "The current game already has two players.",
        "already_authenticated": "This connection is already signed in.",
    }

    def __init__(
        self,
        register: Callable[[str, str], dict[str, Any]],
        login: Callable[[str, str], dict[str, Any]],
        on_login_success: Callable[[], None],
    ) -> None:
        self._register = register
        self._login = login
        self._on_login_success = on_login_success
        self._response_queue: queue.Queue[dict[str, Any]] = queue.Queue()
        self._request_in_progress = False
        self._closed = False
        self._root = tk.Tk()
        self._root.title("Kung Fu Chess - Login")
        self._root.resizable(False, False)
        apply_desktop_theme(self._root)
        self._username = tk.StringVar()
        self._password = tk.StringVar()
        self._status = tk.StringVar(value="●  Log in or create an account.")
        self._build_widgets()
        self._root.protocol("WM_DELETE_WINDOW", self._close)
        self._root.after(50, self._poll_responses)
        fit_and_center(self._root, 440)

    def run(self) -> None:
        """Run the login window until login succeeds or the user closes it."""
        self._root.mainloop()

    def _build_widgets(self) -> None:
        outer = ttk.Frame(self._root, style="App.TFrame", padding=18)
        outer.grid(sticky="nsew")
        frame = ttk.Frame(outer, style="Card.TFrame", padding=32)
        frame.grid(sticky="nsew")
        frame.columnconfigure((0, 1), weight=1, uniform="actions")
        ttk.Label(frame, text="Kung Fu Chess", style="Title.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w"
        )
        ttk.Label(
            frame,
            text="Sign in to enter the multiplayer arena.",
            style="Subtitle.TLabel",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(5, 26))
        ttk.Label(frame, text="Username", style="Field.TLabel").grid(
            row=2, column=0, columnspan=2, sticky="w"
        )
        username_entry = ttk.Entry(
            frame, textvariable=self._username, width=36, style="App.TEntry"
        )
        username_entry.grid(
            row=3, column=0, columnspan=2, pady=(7, 16), sticky="ew"
        )
        ttk.Label(frame, text="Password", style="Field.TLabel").grid(
            row=4, column=0, columnspan=2, sticky="w"
        )
        self._password_entry = ttk.Entry(
            frame,
            textvariable=self._password,
            show="•",
            width=36,
            style="App.TEntry",
        )
        self._password_entry.grid(
            row=5, column=0, columnspan=2, pady=(7, 22), sticky="ew"
        )
        self._login_button = ttk.Button(
            frame,
            text="Login",
            command=lambda: self._submit("login"),
        )
        self._login_button.configure(style="Primary.TButton")
        self._login_button.grid(row=6, column=0, padx=(0, 6), sticky="ew")
        self._register_button = ttk.Button(
            frame,
            text="Register",
            command=lambda: self._submit("register"),
        )
        self._register_button.configure(style="Secondary.TButton")
        self._register_button.grid(row=6, column=1, padx=(6, 0), sticky="ew")
        self._status_label = ttk.Label(
            frame,
            textvariable=self._status,
            style="Info.TLabel",
            wraplength=350,
            anchor="center",
            justify="center",
        )
        self._status_label.grid(
            row=7, column=0, columnspan=2, pady=(18, 0), sticky="ew"
        )
        self._root.bind("<Return>", lambda _event: self._submit("login"))
        username_entry.focus_set()

    def _submit(self, action: str) -> None:
        if self._request_in_progress or self._closed:
            return
        username = self._username.get()
        password = self._password.get()
        self._request_in_progress = True
        self._set_buttons_enabled(False)
        self._status_label.configure(style="Info.TLabel")
        self._status.set("●  Contacting server...")
        callback = self._login if action == "login" else self._register
        threading.Thread(
            target=self._perform_request,
            args=(callback, username, password),
            daemon=True,
        ).start()

    def _perform_request(
        self,
        callback: Callable[[str, str], dict[str, Any]],
        username: str,
        password: str,
    ) -> None:
        try:
            response = callback(username, password)
        except Exception:
            response = {"type": "server_error"}
        self._response_queue.put(response)

    def _poll_responses(self) -> None:
        """Transfer completed worker results onto the Tk event thread."""
        if self._closed:
            return
        try:
            response = self._response_queue.get_nowait()
        except queue.Empty:
            self._root.after(50, self._poll_responses)
            return
        self._handle_response(response)
        if not self._closed:
            self._root.after(50, self._poll_responses)

    def _handle_response(self, response: dict[str, Any]) -> None:
        response_type = str(response.get("type"))
        self._password.set("")
        if response_type == "login_success":
            self._closed = True
            self._root.destroy()
            self._on_login_success()
            return
        is_success = response_type == "registration_success"
        icon = "✓" if is_success else "!"
        message = self._MESSAGES.get(response_type, "Authentication failed.")
        self._status.set(f"{icon}  {message}")
        status_style = "Success.TLabel" if is_success else "Error.TLabel"
        self._status_label.configure(style=status_style)
        self._request_in_progress = False
        self._set_buttons_enabled(True)
        self._password_entry.focus_set()

    def _close(self) -> None:
        """Close safely even if an authentication request is still running."""
        if self._closed:
            return
        self._closed = True
        self._root.destroy()

    def _set_buttons_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        self._login_button.configure(state=state)
        self._register_button.configure(state=state)
