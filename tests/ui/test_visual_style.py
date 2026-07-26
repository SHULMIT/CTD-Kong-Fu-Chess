"""Focused tests for reusable OpenCV presentation primitives."""

import numpy as np

from view.ui.render.visual_style import draw_rounded_panel, draw_status_icon


def test_rounded_panel_changes_panel_center_but_preserves_outer_corner() -> None:
    image = np.zeros((100, 120, 3), dtype=np.uint8)

    draw_rounded_panel(image, 20, 15, 80, 60, radius=12, opacity=1.0)

    assert image[45, 60].any()
    assert not image[15, 20].any()


def test_rounded_panel_ignores_non_positive_dimensions() -> None:
    image = np.zeros((20, 20, 3), dtype=np.uint8)

    draw_rounded_panel(image, 2, 2, 0, 10)

    assert not image.any()


def test_status_icon_draws_inside_requested_radius() -> None:
    image = np.zeros((60, 60, 3), dtype=np.uint8)

    draw_status_icon(image, (30, 30), (100, 150, 200), "!")

    assert image[30, 30].any()
    assert not image[5, 5].any()
