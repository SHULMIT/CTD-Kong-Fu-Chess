"""Expected authentication failures mapped to safe network responses."""


class AuthenticationError(Exception):
    """Base class for expected authentication failures.

    מייצגת את רכיב השרת ``AuthenticationError`` ומרכזת את התנהגותו.

    Responsibility: Base class for expected authentication failures.

    אחריות: מייצגת את רכיב השרת ``AuthenticationError`` ומרכזת את התנהגותו."""


class AuthenticationValidationError(AuthenticationError):
    """Raised when username or password structure is invalid.

    מייצגת את רכיב השרת ``AuthenticationValidationError`` ומרכזת את התנהגותו.

    Responsibility: Raised when username or password structure is invalid.

    אחריות: מייצגת את רכיב השרת ``AuthenticationValidationError`` ומרכזת את התנהגותו."""


class UsernameTakenError(AuthenticationError):
    """Raised when registration uses an existing username.

    מייצגת את רכיב השרת ``UsernameTakenError`` ומרכזת את התנהגותו.

    Responsibility: Raised when registration uses an existing username.

    אחריות: מייצגת את רכיב השרת ``UsernameTakenError`` ומרכזת את התנהגותו."""


class InvalidCredentialsError(AuthenticationError):
    """Raised when login credentials don't identify a user.

    מייצגת את רכיב השרת ``InvalidCredentialsError`` ומרכזת את התנהגותו.

    Responsibility: Raised when login credentials don't identify a user.

    אחריות: מייצגת את רכיב השרת ``InvalidCredentialsError`` ומרכזת את התנהגותו."""
