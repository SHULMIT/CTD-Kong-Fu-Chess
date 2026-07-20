"""Thread-safe spectator membership independent of transport and gameplay."""

from dataclasses import dataclass
import threading

from authentication.user import User


@dataclass(frozen=True)
class SpectatableGame:
    """Public server-authoritative metadata for one active game."""

    game_id: str
    white: User
    black: User


class SpectatorService:
    """Tracks active game metadata and read-only viewers."""

    def __init__(self) -> None:
        self._games: dict[str, SpectatableGame] = {}
        self._spectators_by_game: dict[str, set[object]] = {}
        self._game_by_spectator: dict[object, str] = {}
        self._lock = threading.RLock()

    def register_game(self, game: SpectatableGame) -> None:
        """Expose a newly started game for spectating."""
        with self._lock:
            self._games[game.game_id] = game
            self._spectators_by_game.setdefault(game.game_id, set())

    def list_games(self) -> tuple[SpectatableGame, ...]:
        """Return a deterministic immutable snapshot of active games."""
        with self._lock:
            return tuple(self._games[key] for key in sorted(self._games))

    def join(self, game_id: object, spectator: object) -> bool:
        """Attach an otherwise-idle connection to an active game."""
        if not isinstance(game_id, str):
            return False
        with self._lock:
            if game_id not in self._games or spectator in self._game_by_spectator:
                return False
            self._spectators_by_game[game_id].add(spectator)
            self._game_by_spectator[spectator] = game_id
            return True

    def leave(self, spectator: object) -> str | None:
        """Remove a spectator without changing the observed game."""
        with self._lock:
            game_id = self._game_by_spectator.pop(spectator, None)
            if game_id is not None:
                self._spectators_by_game.get(game_id, set()).discard(spectator)
            return game_id

    def is_spectator(self, connection: object) -> bool:
        with self._lock:
            return connection in self._game_by_spectator

    def spectators_for(self, game_id: str) -> tuple[object, ...]:
        with self._lock:
            return tuple(self._spectators_by_game.get(game_id, ()))

    def close_game(self, game_id: str) -> tuple[object, ...]:
        """Remove an ended game and return viewers that must close their view."""
        with self._lock:
            self._games.pop(game_id, None)
            spectators = tuple(self._spectators_by_game.pop(game_id, ()))
            for spectator in spectators:
                self._game_by_spectator.pop(spectator, None)
            return spectators
