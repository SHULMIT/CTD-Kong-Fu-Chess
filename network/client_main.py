"""Executable entry point for the local multiplayer desktop client."""

import argparse
from collections.abc import Sequence

from app.multiplayer_desktop_application_factory import (
    MultiplayerDesktopApplicationFactory,
)
from network.network_client import NetworkClient
from view.auth.login_window import LoginWindow
from view.auth.multiplayer_menu_window import MultiplayerMenuWindow


def main(arguments: Sequence[str] | None = None) -> None:
    """Connect to a local server and run the existing desktop GUI."""
    parser = argparse.ArgumentParser(description="Run a Kung Fu Chess client.")
    parser.add_argument("--uri", default="ws://127.0.0.1:8765")
    options = parser.parse_args(arguments)
    network_client = NetworkClient(options.uri)
    network_client.connect()

    def open_game() -> None:
        MultiplayerDesktopApplicationFactory.create(network_client).run()

    def open_lobby() -> None:
        MultiplayerMenuWindow(network_client, open_game).run()

    login_window = LoginWindow(
        register=network_client.register,
        login=network_client.login,
        on_login_success=open_lobby,
    )
    try:
        login_window.run()
    finally:
        network_client.disconnect()


if __name__ == "__main__":
    main()
