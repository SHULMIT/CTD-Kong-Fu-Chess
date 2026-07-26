"""Transport-facing authentication workflow and authenticated client context."""

import asyncio
import logging

from authentication.authentication_service import AuthenticationService
from authentication.errors import (
    AuthenticationValidationError,
    InvalidCredentialsError,
    UsernameTakenError,
)
from authentication.user import User
from network.server.transport.client_messenger import ClientMessenger, MessageConnection
from network.server.transport.game_snapshot_serializer import JsonValue


class AuthenticationHandler:
    """Maps authentication messages to the service and owns client identities.

    ממפה הודעות אימות לשירות ומנהלת את זהויות הלקוחות.

    Responsibility: Maps authentication messages to the service and owns client identities.

    אחריות: ממפה הודעות אימות לשירות ומנהלת את זהויות הלקוחות."""

    def __init__(
        self,
        service: AuthenticationService | None,
        messenger: ClientMessenger,
        logger: logging.Logger,
    ) -> None:
        """Initialize the instance and its dependencies.

        מאתחלת את המופע ואת התלויות שלו."""
        self.service = service
        self.users: dict[object, User] = {}
        self._messenger = messenger
        self._logger = logger

    async def handle(
        self,
        connection: MessageConnection,
        message: dict[str, object],
    ) -> None:
        """Register or log in and preserve all existing response mappings.

        רושמת או מחברת משתמש ושומרת על מיפויי התגובות הקיימים."""
        if self.service is None:
            return
        username = message.get("username")
        password = message.get("password")
        try:
            if message["type"] == "register":
                user = await asyncio.to_thread(self.service.register, username, password)
                await self._messenger.send(
                    connection, self.response("registration_success", user)
                )
                self._log(logging.INFO, "registration_succeeded", user)
                return
            user = await asyncio.to_thread(self.service.login, username, password)
            self.attach(connection, user)
            await self._messenger.send(connection, self.response("login_success", user))
            self._log(logging.INFO, "login_succeeded", user)
        except UsernameTakenError:
            self._log(logging.WARNING, "registration_failed", reason="username_taken")
            await self._messenger.send(connection, {"type": "username_taken"})
        except InvalidCredentialsError:
            self._log(logging.WARNING, "login_failed", reason="invalid_credentials")
            await self._messenger.send(connection, {"type": "invalid_credentials"})
        except AuthenticationValidationError:
            self._log(logging.WARNING, "authentication_validation_failed")
            await self._messenger.send(connection, {"type": "validation_error"})
        except Exception:
            self._logger.exception("Unexpected authentication server error")
            await self._messenger.send(connection, {"type": "server_error"})

    async def refresh(self, connection: object) -> User | None:
        """Refresh one authenticated user's authoritative persistent profile.

        מרעננת את הפרופיל המתמשך והסמכותי של משתמש מאומת אחד."""
        if self.service is None:
            return None
        authenticated = self.users[connection]
        current = await asyncio.to_thread(
            self.service.current_user, authenticated.username
        )
        if current is not None:
            self.attach(connection, current)
        return current

    def attach(self, connection: object, user: User) -> None:
        """Associate an authenticated identity with its current connection.

        מקשרת זהות מאומתת לחיבור הנוכחי שלה."""
        self.users[connection] = user

    def remove(self, connection: object) -> User | None:
        """Remove and return the identity associated with a connection.

        מסירה ומחזירה את הזהות המשויכת לחיבור."""
        return self.users.pop(connection, None)

    def lookup(self, connection: object) -> User | None:
        """Return the authenticated identity for a connection, if present.

        מחזירה את הזהות המאומתת של חיבור, אם קיימת."""
        return self.users.get(connection)

    def replace(self, updated_user: User) -> None:
        """Replace cached copies of a persistently updated user.

        מחליפה עותקי מטמון של משתמש שעודכן בשמירה המתמשכת."""
        for connection, user in self.users.items():
            if user.id == updated_user.id:
                self.users[connection] = updated_user
                return

    @staticmethod
    def response(response_type: str, user: User) -> dict[str, JsonValue]:
        """Build a standard authentication response for a user.

        יוצרת תגובת אימות תקנית עבור משתמש."""
        return {"type": response_type, "username": user.username, "rating": user.rating}

    def _log(
        self,
        level: int,
        event_type: str,
        user: User | None = None,
        reason: str | None = None,
    ) -> None:
        """Write a structured server event to the configured logger.

        כותבת אירוע שרת מובנה ללוגר שהוגדר."""
        context: dict[str, object] = {"event_type": event_type}
        if user is not None:
            context.update(user_id=user.id, username=user.username)
        if reason is not None:
            context["reason"] = reason
        self._logger.log(level, event_type, extra=context)
