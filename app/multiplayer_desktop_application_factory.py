"""Composition root for the remote multiplayer desktop client."""

from app.game_application import GameApplication
from network.multiplayer_controller import MultiplayerController
from network.network_client import NetworkClient
from network.remote_game_state import RemoteGameState
from view.ui.scene.game_scene_factory import GameSceneFactory


class MultiplayerDesktopApplicationFactory:
    """Builds the existing desktop UI around server-authoritative state."""

    @staticmethod
    def create(network_client: NetworkClient) -> GameApplication:
        """Build the game UI around an already authenticated connection."""
        game_state = RemoteGameState(network_client)
        if network_client.match_found is not None:
            game_state.apply_message(network_client.match_found)
        if network_client.initial_snapshot is not None:
            game_state.apply_message(
                {"type": "game_snapshot", "state": network_client.initial_snapshot}
            )
        if network_client.player_profiles is not None:
            game_state.apply_message(network_client.player_profiles)
        game_state.wait(0)
        game_state.set_local_profile(
            color=network_client.assigned_color,
            username=network_client.username,
            rating=network_client.rating,
        )
        controller = MultiplayerController(game_state, network_client)
        scene = GameSceneFactory.create(
            controller=controller,
            game_engine=game_state,
        )
        return GameApplication(
            scene=scene,
            on_close=network_client.disconnect,
        )
