"""Fast localhost integration test for the actual WebSocket transport."""

import asyncio
import json

from app.game_engine_factory import GameEngineFactory
from network.server.game_server import GameServer
from websockets.asyncio.client import connect
from websockets.asyncio.server import serve


def test_real_localhost_connections_receive_assignments_and_rejection() -> None:
    async def scenario() -> None:
        game_server = GameServer(GameEngineFactory.create())
        async with serve(game_server.handle_client, "127.0.0.1", 0) as server:
            port = server.sockets[0].getsockname()[1]
            uri = f"ws://127.0.0.1:{port}"
            async with connect(uri, proxy=None) as first:
                assert json.loads(await first.recv()) == {
                    "type": "connection_accepted",
                    "color": "white",
                }
                assert json.loads(await first.recv())["type"] == "game_snapshot"

                async with connect(uri, proxy=None) as second:
                    assert json.loads(await second.recv()) == {
                        "type": "connection_accepted",
                        "color": "black",
                    }
                    assert json.loads(await second.recv())["type"] == "game_snapshot"

                    async with connect(uri, proxy=None) as third:
                        assert json.loads(await third.recv()) == {
                            "type": "connection_rejected",
                            "reason": "game_full",
                        }

    asyncio.run(scenario())
