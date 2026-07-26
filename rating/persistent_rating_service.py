"""Application service for idempotent persisted multiplayer ratings."""

from dataclasses import dataclass

from authentication.user import User
from authentication.user_repository import UserRepository
from rating.elo_rating_service import EloRatingService


@dataclass(frozen=True)
class RatingUpdate:
    """Authoritative user ratings after one persisted game result.

    מייצגת את רכיב השרת ``RatingUpdate`` ומרכזת את התנהגותו.

    Responsibility: Authoritative user ratings after one persisted game result.

    אחריות: מייצגת את רכיב השרת ``RatingUpdate`` ומרכזת את התנהגותו."""

    winner: User
    loser: User
    winner_change: int
    loser_change: int


class PersistentRatingService:
    """Calculates and atomically persists one decisive result per game ID.

    מייצגת את רכיב השרת ``PersistentRatingService`` ומרכזת את התנהגותו.

    Responsibility: Calculates and atomically persists one decisive result per game ID.

    אחריות: מייצגת את רכיב השרת ``PersistentRatingService`` ומרכזת את התנהגותו."""

    def __init__(
        self,
        repository: UserRepository,
        elo_service: EloRatingService,
    ) -> None:
        """Initialize the instance and its dependencies.

        מאתחלת את המופע ואת התלויות שלו."""
        self._repository = repository
        self._elo_service = elo_service

    def record_result(
        self,
        game_id: str,
        winner: User,
        loser: User,
    ) -> RatingUpdate | None:
        """Persist a decisive result, or return ``None`` if already recorded.

        מבצעת את פעולת ``record`` התוצאה."""
        result = self._elo_service.calculate(winner.rating, loser.rating)
        persisted = self._repository.apply_rating_update(
            game_id=game_id,
            winner_id=winner.id,
            loser_id=loser.id,
            winner_rating=result.winner_rating,
            loser_rating=result.loser_rating,
        )
        if not persisted:
            return None
        return RatingUpdate(
            winner=User(winner.id, winner.username, result.winner_rating),
            loser=User(loser.id, loser.username, result.loser_rating),
            winner_change=result.rating_change,
            loser_change=-result.rating_change,
        )
