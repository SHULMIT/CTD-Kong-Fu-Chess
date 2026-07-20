"""Expected authentication failures mapped to safe network responses."""


class AuthenticationError(Exception):
    """Base class for expected authentication failures."""


class AuthenticationValidationError(AuthenticationError):
    """Raised when username or password structure is invalid."""


class UsernameTakenError(AuthenticationError):
    """Raised when registration uses an existing username."""


class InvalidCredentialsError(AuthenticationError):
    """Raised when login credentials don't identify a user."""
