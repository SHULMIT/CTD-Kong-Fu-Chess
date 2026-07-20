"""Versioned scrypt password hashing with per-password random salts."""

import base64
import hashlib
import hmac
import os


class ScryptPasswordHasher:
    """Hashes and verifies passwords using the memory-hard scrypt KDF."""

    _N = 2**14
    _R = 8
    _P = 5
    _SALT_BYTES = 16
    _KEY_BYTES = 64
    _MAX_MEMORY = 32 * 1024 * 1024

    def hash(self, password: str) -> str:
        """Return a versioned encoded hash; never retain plaintext input."""
        salt = os.urandom(self._SALT_BYTES)
        digest = self._derive(password, salt, self._N, self._R, self._P)
        return "$".join(
            (
                "scrypt",
                str(self._N),
                str(self._R),
                str(self._P),
                base64.b64encode(salt).decode("ascii"),
                base64.b64encode(digest).decode("ascii"),
            )
        )

    def verify(self, password: str, encoded_hash: str) -> bool:
        """Verify a password against a stored versioned hash."""
        try:
            algorithm, n, r, p, encoded_salt, encoded_digest = (
                encoded_hash.split("$")
            )
            if algorithm != "scrypt":
                return False
            salt = base64.b64decode(encoded_salt, validate=True)
            expected = base64.b64decode(encoded_digest, validate=True)
            actual = self._derive(password, salt, int(n), int(r), int(p))
        except (ValueError, TypeError):
            return False
        return hmac.compare_digest(actual, expected)

    @classmethod
    def _derive(
        cls,
        password: str,
        salt: bytes,
        n: int,
        r: int,
        p: int,
    ) -> bytes:
        return hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=n,
            r=r,
            p=p,
            maxmem=cls._MAX_MEMORY,
            dklen=cls._KEY_BYTES,
        )
