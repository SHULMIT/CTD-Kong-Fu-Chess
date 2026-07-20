"""Tk desktop login and registration window for multiplayer mode."""

from collections.abc import Callable
import threading
import tkinter as tk
from tkinter import ttk
from typing import Any


class LoginWindow:
    """Collects credentials and displays safe structured auth responses."""

    _MESSAGES = {
        "registration_success": "Registration succeeded. You can now log in.",
        "username_taken": "That username is already taken.",
        "invalid_credentials": "Invalid username or password.",
        "validation_error": (
            "Username: 3-32 letters, numbers or _. Password: 8-128 characters."
        ),
        "server_error": "The server encountered an error. Please try again.",
        "connection_rejected": "The current game already has two players.",
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
        self._root = tk.Tk()
        self._root.title("Kung Fu Chess - Login")
        self._root.resizable(False, False)
        self._username = tk.StringVar()
        self._password = tk.StringVar()
        self._status = tk.StringVar(value="Log in or create an account.")
        self._build_widgets()

    def run(self) -> None:
        """Run the login window until login succeeds or the user closes it."""
        self._root.mainloop()

    def _build_widgets(self) -> None:
        frame = ttk.Frame(self._root, padding=24)
        frame.grid()
        ttk.Label(frame, text="Username").grid(row=0, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self._username, width=32).grid(
            row=1, column=0, columnspan=2, pady=(4, 12)
        )
        ttk.Label(frame, text="Password").grid(row=2, column=0, sticky="w")
        ttk.Entry(
            frame,
            textvariable=self._password,
            show="*",
            width=32,
        ).grid(row=3, column=0, columnspan=2, pady=(4, 16))
        self._login_button = ttk.Button(
            frame,
            text="Login",
            command=lambda: self._submit("login"),
        )
        self._login_button.grid(row=4, column=0, padx=(0, 6), sticky="ew")
        self._register_button = ttk.Button(
            frame,
            text="Register",
            command=lambda: self._submit("register"),
        )
        self._register_button.grid(row=4, column=1, padx=(6, 0), sticky="ew")
        ttk.Label(
            frame,
            textvariable=self._status,
            wraplength=320,
        ).grid(row=5, column=0, columnspan=2, pady=(16, 0))

    def _submit(self, action: str) -> None:
        username = self._username.get()
        password = self._password.get()
        self._set_buttons_enabled(False)
        self._status.set("Contacting server...")
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
        self._root.after(0, self._handle_response, response)

    def _handle_response(self, response: dict[str, Any]) -> None:
        response_type = str(response.get("type"))
        self._password.set("")
        if response_type == "login_success":
            self._root.destroy()
            self._on_login_success()
            return
        self._status.set(
            self._MESSAGES.get(response_type, "Authentication failed.")
        )
        self._set_buttons_enabled(True)

    def _set_buttons_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        self._login_button.configure(state=state)
        self._register_button.configure(state=state)
