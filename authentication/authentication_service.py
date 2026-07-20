"""Credential validation and account registration business service."""

import re

from authentication.errors import (
    AuthenticationValidationError,
    InvalidCredentialsError,
)
from authentication.password_hasher import ScryptPasswordHasher
from authentication.user import User
from authentication.user_repository import UserRepository


class AuthenticationService:
    """Registers and authenticates users without transport dependencies."""

    INITIAL_RATING = 1200
    _USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_]{3,32}$")

    def __init__(
        self,
        repository: UserRepository,
        password_hasher: ScryptPasswordHasher | None = None,
    ) -> None:
        self._repository = repository
        self._password_hasher = password_hasher or ScryptPasswordHasher()

    def initialize(self) -> None:
        """Initialize persistence without destroying existing accounts."""
        self._repository.initialize()

    def register(self, username: object, password: object) -> User:
        """Validate and create a uniquely named account."""
        username_value, password_value = self._validate(username, password)
        password_hash = self._password_hasher.hash(password_value)
        return self._repository.create(
            username_value,
            password_hash,
            self.INITIAL_RATING,
        )

    def login(self, username: object, password: object) -> User:
        """Return the authenticated account or raise a safe credential error."""
        username_value, password_value = self._validate(username, password)
        stored_user = self._repository.find_by_username(username_value)
        if stored_user is None or not self._password_hasher.verify(
            password_value,
            stored_user.password_hash,
        ):
            raise InvalidCredentialsError()
        return stored_user.user

    def current_user(self, username: str) -> User | None:
        """Return the latest persisted public profile for an authenticated name."""
        stored_user = self._repository.find_by_username(username)
        return stored_user.user if stored_user is not None else None

    @classmethod
    def _validate(cls, username: object, password: object) -> tuple[str, str]:
        if not isinstance(username, str) or not isinstance(password, str):
            raise AuthenticationValidationError()
        if cls._USERNAME_PATTERN.fullmatch(username) is None:
            raise AuthenticationValidationError()
        if not 8 <= len(password) <= 128:
            raise AuthenticationValidationError()
        return username, password
