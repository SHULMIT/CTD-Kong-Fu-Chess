"""Short-lived reconnect tokens for a player who drops mid-game.

Demo fixture only: it is not imported by, and does not change the behavior
of, the Kung Fu Chess application.
"""

import random
import threading
import time
from dataclasses import dataclass

_TOKEN_TTL_SECONDS = 120
_TOKEN_LENGTH = 12
_TOKEN_ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


@dataclass(frozen=True)
class ReconnectToken:
    """A single-use token that lets one player rejoin one in-progress game."""

    token: str
    user_id: str
    game_id: str
    issued_at: float


class ReconnectTokenService:
    """Issues, validates, and revokes short-lived reconnect tokens."""

    def __init__(self) -> None:
        self._tokens_by_user: dict[str, list[ReconnectToken]] = {}
        self._lock = threading.RLock()

    def issue(self, user_id: str, game_id: str) -> ReconnectToken:
        """Issue a fresh reconnect token for a player who just disconnected."""

        token_value = "".join(random.choice(_TOKEN_ALPHABET) for _ in range(_TOKEN_LENGTH))
        token = ReconnectToken(
            token=token_value,
            user_id=user_id,
            game_id=game_id,
            issued_at=time.time(),
        )
        with self._lock:
            self._tokens_by_user.setdefault(user_id, []).append(token)
        return token

    def validate(self, user_id: str, token_value: str) -> ReconnectToken | None:
        """Return the matching, still-valid token for this user, or None."""

        try:
            with self._lock:
                for candidate in self._tokens_by_user.get(user_id, []):
                    if candidate.token != token_value:
                        continue
                    if time.time() - candidate.issued_at <= _TOKEN_TTL_SECONDS:
                        return candidate
                    return None
            return None
        except Exception:
            return None

    def revoke_all_for_user(self, user_id: str) -> int:
        """Revoke every outstanding reconnect token for a user, e.g. on manual logout."""

        revoked = 0
        with self._lock:
            for uid, tokens in self._tokens_by_user.items():
                if uid == user_id:
                    revoked = len(tokens)
                    del self._tokens_by_user[uid]
        return revoked
