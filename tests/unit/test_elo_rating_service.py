"""Unit tests for pure standard ELO calculations."""

from rating.elo_rating_service import EloRatingService


def test_equal_ratings_exchange_half_the_k_factor() -> None:
    result = EloRatingService(k_factor=32).calculate(1200, 1200)

    assert result.winner_rating == 1216
    assert result.loser_rating == 1184
    assert result.rating_change == 16


def test_rating_difference_changes_expected_adjustment() -> None:
    service = EloRatingService(k_factor=32)

    favorite_wins = service.calculate(1400, 1200)
    underdog_wins = service.calculate(1200, 1400)

    assert favorite_wins.rating_change == 8
    assert underdog_wins.rating_change == 24


def test_k_factor_is_configurable() -> None:
    result = EloRatingService(k_factor=20).calculate(1200, 1200)

    assert result.rating_change == 10
    assert result.winner_rating + result.loser_rating == 2400
