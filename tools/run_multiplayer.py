"""Launch one local server and two authenticated desktop clients."""

from __future__ import annotations

import socket
import subprocess
import sys
import time


HOST = "127.0.0.1"
PORT = 8765
SERVER_START_TIMEOUT_SECONDS = 10.0


def main() -> int:
    """Run the complete local multiplayer setup until both clients close."""
    if _is_port_open():
        print(f"Port {PORT} is already in use. Close the old server and try again.")
        return 1

    server = _start_process("network.server.main", hide_window=True)
    clients: list[subprocess.Popen] = []
    try:
        if not _wait_for_server(server):
            print("The local game server failed to start.")
            return 1

        clients = [
            _start_process("network.client_main"),
            _start_process("network.client_main"),
        ]
        print("Kung Fu Chess is running. Log in from both client windows.")
        for client in clients:
            client.wait()
        return 0
    except KeyboardInterrupt:
        return 0
    finally:
        for client in clients:
            _stop_process(client)
        _stop_process(server)


def _start_process(module: str, hide_window: bool = False) -> subprocess.Popen:
    creation_flags = 0
    if hide_window and sys.platform == "win32":
        creation_flags = subprocess.CREATE_NO_WINDOW
    return subprocess.Popen(
        [sys.executable, "-m", module],
        creationflags=creation_flags,
    )


def _wait_for_server(server: subprocess.Popen) -> bool:
    deadline = time.monotonic() + SERVER_START_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        if server.poll() is not None:
            return False
        if _is_port_open():
            return True
        time.sleep(0.1)
    return False


def _is_port_open() -> bool:
    try:
        with socket.create_connection((HOST, PORT), timeout=0.2):
            return True
    except OSError:
        return False


def _stop_process(process: subprocess.Popen) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=3)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


if __name__ == "__main__":
    raise SystemExit(main())
