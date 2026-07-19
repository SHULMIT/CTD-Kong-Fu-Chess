"""Tests for game-scene coordination."""

from unittest.mock import Mock, call

from view.ui.scene.game_scene import GameScene


def test_draw_coordinates_layers_in_the_required_order() -> None:
    calls = Mock()
    canvas = calls.canvas
    board_renderer = calls.board_renderer
    piece_layer_renderer = calls.piece_layer_renderer
    player_activity_renderer = calls.player_activity_renderer
    status_message_controller = calls.status_message_controller
    overlay_renderer = calls.overlay_renderer
    controller = Mock(selected_position=None)
    game_engine = Mock(
        board="board",
        game_over=False,
    )
    game_engine.get_motions.return_value = ("motion",)

    scene = GameScene(
        controller=controller,
        game_engine=game_engine,
        canvas=canvas,
        layout=Mock(),
        input_handler=Mock(),
        board_renderer=board_renderer,
        piece_layer_renderer=piece_layer_renderer,
        player_activity_renderer=player_activity_renderer,
        overlay_renderer=overlay_renderer,
        status_message_controller=status_message_controller,
    )

    scene.draw()

    assert calls.mock_calls == [
        call.canvas.reset(),
        call.board_renderer.draw(),
        call.piece_layer_renderer.draw("board", ("motion",)),
        call.player_activity_renderer.draw(),
        call.status_message_controller.draw(),
        call.overlay_renderer.draw_selected(None),
    ]
