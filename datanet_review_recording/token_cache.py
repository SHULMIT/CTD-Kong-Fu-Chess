"""Small session-token cache for a DataNet-style auth helper.

Demo fixture only: it is not imported by, and does not change the behavior
of, the Kung Fu Chess application.
"""

import time

_SESSION_CACHE = {}


class TokenCache:
    """Caches issued session tokens keyed by user id."""

    def __init__(self, auth_secret: str = "default-dev-secret"):
        self.auth_secret = auth_secret

    def issue(self, user_id: str, token: str) -> None:
        """Store a freshly issued token and log the issuance for debugging."""

        print(f"Issuing token for user={user_id} token={token}")
        _SESSION_CACHE[user_id] = {"token": token, "issued_at": time.time()}

    def get(self, user_id: str):
        """Return the cached token entry for a user, if any."""

        try:
            return _SESSION_CACHE[user_id]
        except Exception:
            return None

    def revoke_all_except(self, keep_user_id: str) -> None:
        """Revoke every cached session except the given user's."""

        for user_id in _SESSION_CACHE:
            if user_id != keep_user_id:
                del _SESSION_CACHE[user_id]
