from view.ui.render.piece_renderer import PieceRenderer


def test_jump_height_starts_and_ends_at_ground_level():
    assert PieceRenderer._get_jump_height(0.0, 100) == 0
    assert PieceRenderer._get_jump_height(0.6, 100) == 0


def test_jump_height_reaches_peak_halfway_through_jump():
    assert PieceRenderer._get_jump_height(0.3, 100) == 35
