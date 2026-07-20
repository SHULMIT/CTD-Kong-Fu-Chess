"""Command-line entry point for the local two-player WebSocket server."""

import argparse
import asyncio
from collections.abc import Sequence

from authentication.authentication_service import AuthenticationService
from authentication.sqlite_user_repository import SQLiteUserRepository
from app.game_engine_factory import GameEngineFactory
from network.game_server import GameServer
from network.reconnect_session_service import ReconnectSessionService
from network.server_logging import configure_server_logging
from rating.elo_rating_service import EloRatingService
from rating.persistent_rating_service import PersistentRatingService


def main(arguments: Sequence[str] | None = None) -> None:
    """Parse local server options and run one authoritative game."""
    parser = argparse.ArgumentParser(description="Run the Kung Fu Chess server.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8765, type=int)
    parser.add_argument("--database", default="data/users.db")
    parser.add_argument("--k-factor", default=32, type=int)
    parser.add_argument("--reconnect-timeout", default=20.0, type=float)
    parser.add_argument("--log-level", default="INFO")
    parser.add_argument("--log-file", default="data/server.log")
    parser.add_argument("--log-max-bytes", default=2_000_000, type=int)
    parser.add_argument("--log-backup-count", default=5, type=int)
    options = parser.parse_args(arguments)
    logger = configure_server_logging(
        level=options.log_level,
        log_file=options.log_file,
        max_bytes=options.log_max_bytes,
        backup_count=options.log_backup_count,
    )
    repository = SQLiteUserRepository(options.database)
    authentication_service = AuthenticationService(repository)
    authentication_service.initialize()
    rating_service = PersistentRatingService(
        repository,
        EloRatingService(k_factor=options.k_factor),
    )
    server = GameServer(
        GameEngineFactory.create(),
        authentication_service=authentication_service,
        rating_service=rating_service,
        reconnect_service=ReconnectSessionService(options.reconnect_timeout),
        logger=logger,
    )
    try:
        asyncio.run(server.run(options.host, options.port))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
