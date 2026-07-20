"""Tests for desktop-only application composition."""

from unittest.mock import patch

from app.desktop_application_factory import DesktopApplicationFactory


def test_create_composes_desktop_application_around_factory_engine() -> None:
    with (
        patch(
            "app.desktop_application_factory.GameEngineFactory.create"
        ) as create_engine,
        patch("app.desktop_application_factory.Controller") as controller_type,
        patch(
            "app.desktop_application_factory.GameSceneFactory.create"
        ) as create_scene,
        patch(
            "app.desktop_application_factory.GameApplication"
        ) as application_type,
    ):
        application = DesktopApplicationFactory.create()

    create_engine.assert_called_once_with()
    controller_type.assert_called_once_with(game_engine=create_engine.return_value)
    create_scene.assert_called_once_with(
        controller=controller_type.return_value,
        game_engine=create_engine.return_value,
    )
    application_type.assert_called_once_with(scene=create_scene.return_value)
    assert application is application_type.return_value
