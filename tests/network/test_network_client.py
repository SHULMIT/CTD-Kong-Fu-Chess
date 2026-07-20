"""Local WebSocket tests for the background multiplayer client."""

import json
import queue
import threading

from model.piece import PieceColor
from model.position import Position
from network.network_client import MultiplayerClientState, NetworkClient
from websockets.exceptions import ConnectionClosed
from websockets.sync.server import serve


INITIAL_STATE = {
    "board": {"width": 1, "height": 1, "pieces": []},
    "motions": [],
    "scores": {"white": 0, "black": 0},
    "game_over": False,
    "winner": None,
}


def test_client_connects_sends_commands_and_receives_server_messages() -> None:
    received_commands: queue.Queue[dict] = queue.Queue()

    def handler(connection) -> None:
        connection.send(json.dumps({"type": "connection_accepted", "color": "white"}))
        connection.send(json.dumps({"type": "game_snapshot", "state": INITIAL_STATE}))
        try:
            received_commands.put(json.loads(connection.recv()))
            received_commands.put(json.loads(connection.recv()))
            received_commands.put(json.loads(connection.recv()))
            connection.send(json.dumps({"type": "command_accepted", "command": "move"}))
            connection.send(json.dumps({"type": "command_rejected", "reason": "not_your_piece"}))
            connection.send(
                json.dumps(
                    {
                        "type": "game_event",
                        "event": {"type": "jump_started", "piece_id": 1},
                    }
                )
            )
            connection.send(json.dumps({"type": "server_error"}))
            connection.send(
                json.dumps(
                    {
                        "type": "legal_moves",
                        "source": {"row": 1, "column": 2},
                        "positions": [{"row": 2, "column": 2}],
                    }
                )
            )
            connection.recv()
        except ConnectionClosed:
            pass

    server = serve(handler, "127.0.0.1", 0)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    port = server.socket.getsockname()[1]
    client = NetworkClient(f"ws://127.0.0.1:{port}")

    try:
        client.connect()
        first_message = client.receive(timeout=2)
        second_message = client.receive(timeout=2)
        assert client.assigned_color is PieceColor.WHITE
        assert client.initial_snapshot == INITIAL_STATE
        assert client.matchmaking_state is MultiplayerClientState.IN_GAME
        assert client.is_connected

        client.send_move(Position(1, 2), Position(3, 4)).result(timeout=2)
        client.send_jump(Position(5, 6)).result(timeout=2)
        client.request_legal_moves(Position(1, 2)).result(timeout=2)

        assert received_commands.get(timeout=2) == {
            "type": "move",
            "source": {"row": 1, "column": 2},
            "target": {"row": 3, "column": 4},
        }
        assert received_commands.get(timeout=2) == {
            "type": "jump",
            "position": {"row": 5, "column": 6},
        }
        assert received_commands.get(timeout=2) == {
            "type": "legal_moves",
            "position": {"row": 1, "column": 2},
        }

        message_types = {first_message["type"], second_message["type"]} | {
            client.receive(timeout=2)["type"]
            for _ in range(5)
        }
        assert message_types == {
            "connection_accepted",
            "game_snapshot",
            "command_accepted",
            "command_rejected",
            "game_event",
            "server_error",
            "legal_moves",
        }
    finally:
        client.disconnect()
        server.shutdown()
        server_thread.join(timeout=2)

    assert not client.is_connected


def test_client_registration_and_login_capture_profile_and_snapshot() -> None:
    def handler(connection) -> None:
        registration = json.loads(connection.recv())
        assert registration["type"] == "register"
        connection.send(
            json.dumps(
                {
                    "type": "registration_success",
                    "username": "Player_1",
                    "rating": 1200,
                }
            )
        )
        login = json.loads(connection.recv())
        assert login["type"] == "login"
        connection.send(
            json.dumps(
                {
                    "type": "login_success",
                    "username": "Player_1",
                    "rating": 1200,
                }
            )
        )
        matchmaking = json.loads(connection.recv())
        assert matchmaking["type"] == "start_matchmaking"
        connection.send(
            json.dumps({"type": "match_found", "game_id": "game-1", "players": []})
        )
        connection.send(
            json.dumps({"type": "connection_accepted", "color": "black"})
        )
        connection.send(
            json.dumps({"type": "game_snapshot", "state": INITIAL_STATE})
        )
        try:
            connection.recv()
        except ConnectionClosed:
            pass

    server = serve(handler, "127.0.0.1", 0)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    client = NetworkClient(
        f"ws://127.0.0.1:{server.socket.getsockname()[1]}"
    )
    try:
        client.connect()

        registration = client.register("Player_1", "password123")
        login = client.login("Player_1", "password123")
        client.start_matchmaking().result(timeout=2)
        assert client.receive(timeout=2)["type"] == "registration_success"
        assert client.receive(timeout=2)["type"] == "login_success"
        assert client.receive(timeout=2)["type"] == "match_found"
        assert client.receive(timeout=2)["type"] == "connection_accepted"
        assert client.receive(timeout=2)["type"] == "game_snapshot"

        assert registration["type"] == "registration_success"
        assert login["type"] == "login_success"
        assert client.username == "Player_1"
        assert client.rating == 1200
        assert client.assigned_color is PieceColor.BLACK
        assert client.initial_snapshot == INITIAL_STATE
        assert client.match_found is not None
        assert client.matchmaking_state is MultiplayerClientState.IN_GAME
    finally:
        client.disconnect()
        server.shutdown()
        server_thread.join(timeout=2)
