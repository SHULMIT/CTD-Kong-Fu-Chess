"""Application service for idempotent persisted multiplayer ratings."""

from dataclasses import dataclass

from authentication.user import User
from authentication.user_repository import UserRepository
from rating.elo_rating_service import EloRatingService


@dataclass(frozen=True)
class RatingUpdate:
    """Authoritative user ratings after one persisted game result."""

    winner: User
    loser: User
    winner_change: int
    loser_change: int


class PersistentRatingService:
    """Calculates and atomically persists one decisive result per game ID."""

    def __init__(
        self,
        repository: UserRepository,
        elo_service: EloRatingService,
    ) -> None:
        self._repository = repository
        self._elo_service = elo_service

    def record_result(
        self,
        game_id: str,
        winner: User,
        loser: User,
    ) -> RatingUpdate | None:
        """Persist a decisive result, or return ``None`` if already recorded."""
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
