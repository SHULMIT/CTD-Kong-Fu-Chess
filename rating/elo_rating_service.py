"""Pure standard ELO rating calculation."""

from dataclasses import dataclass


@dataclass(frozen=True)
class EloResult:
    """New ratings and the zero-sum change for a decisive result."""

    winner_rating: int
    loser_rating: int
    rating_change: int


class EloRatingService:
    """Calculates decisive-game ratings with a configurable K-factor."""

    def __init__(self, k_factor: int = 32) -> None:
        if k_factor <= 0:
            raise ValueError("K-factor must be positive.")
        self._k_factor = k_factor

    @property
    def k_factor(self) -> int:
        """Return the configured maximum rating adjustment."""
        return self._k_factor

    def calculate(self, winner_rating: int, loser_rating: int) -> EloResult:
        """Return zero-sum ELO updates for a winner and loser."""
        expected_winner = 1 / (
            1 + 10 ** ((loser_rating - winner_rating) / 400)
        )
        rating_change = round(self._k_factor * (1 - expected_winner))
        return EloResult(
            winner_rating=winner_rating + rating_change,
            loser_rating=loser_rating - rating_change,
            rating_change=rating_change,
        )
