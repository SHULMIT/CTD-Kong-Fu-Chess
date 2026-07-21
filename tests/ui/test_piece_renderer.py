from view.ui.animation.piece_animation_service import PieceAnimationService


def test_jump_height_starts_and_ends_at_ground_level():
    assert PieceAnimationService._calculate_jump_height(0.0, 100) == 0
    assert PieceAnimationService._calculate_jump_height(0.6, 100) == 0


def test_jump_height_reaches_peak_halfway_through_jump():
    assert PieceAnimationService._calculate_jump_height(0.3, 100) == 35
