"""Composition tests for multiplayer GUI mode."""

from unittest.mock import patch

from app.multiplayer_desktop_application_factory import (
    MultiplayerDesktopApplicationFactory,
)


def test_factory_uses_remote_state_without_creating_game_engine() -> None:
    with (
        patch(
            "app.multiplayer_desktop_application_factory.NetworkClient"
        ) as client_type,
        patch(
            "app.multiplayer_desktop_application_factory.RemoteGameState"
        ) as state_type,
        patch(
            "app.multiplayer_desktop_application_factory.MultiplayerController"
        ) as controller_type,
        patch(
            "app.multiplayer_desktop_application_factory.GameSceneFactory.create"
        ) as create_scene,
        patch(
            "app.multiplayer_desktop_application_factory.GameApplication"
        ) as application_type,
    ):
        application = MultiplayerDesktopApplicationFactory.create(
            client_type.return_value
        )

    client = client_type.return_value
    state = state_type.return_value
    state_type.assert_called_once_with(client)
    state.wait.assert_called_once_with(0)
    state.set_local_profile.assert_called_once_with(
        color=client.assigned_color,
        username=client.username,
        rating=client.rating,
    )
    controller_type.assert_called_once_with(state, client)
    create_scene.assert_called_once_with(
        controller=controller_type.return_value,
        game_engine=state,
    )
    application_type.assert_called_once_with(
        scene=create_scene.return_value,
        on_close=client.disconnect,
    )
    assert application is application_type.return_value
