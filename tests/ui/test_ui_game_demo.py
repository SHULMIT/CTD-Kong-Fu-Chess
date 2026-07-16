"""Integration coverage for sprite loading and the complete UI game demo."""

from pathlib import Path

import numpy as np

from model.piece import Piece, PieceColor, PieceType
from model.position import Position
from board_io.text_board_parser import TextBoardParser
from controller.controller import Controller
from game.game_engine import GameEngine
from realtime.duration_calculator import DurationCalculator
from realtime.real_time_arbiter import RealTimeArbiter
from rules.rule_engine import RuleEngine
from run_ui_game_demo import FRAMES_PER_MOVE, _game_moves, render_game_demo
from view.ui.animation.animation_repository import AnimationRepository
from view.ui.animation.animation_state import AnimationState
from view.ui.animation.piece_code_resolver import PieceCodeResolver
from view.ui.graphics.img import Img
from view.ui.scene.game_scene import GameScene


def _create_scene(board):
    game_engine = GameEngine(
        board=board,
        rule_engine=RuleEngine(),
        arbiter=RealTimeArbiter(board),
        duration_calculator=DurationCalculator(),
    )
    controller = Controller(game_engine)
    return GameScene(controller=controller, game_engine=game_engine)


def test_piece_animation_is_resolved_loaded_and_cached():
    piece = Piece(1, PieceType.KNIGHT, PieceColor.WHITE, Position(7, 6))
    assert PieceCodeResolver.resolve(piece) == "NW"

    repository = AnimationRepository()
    animation = repository.get("NW", AnimationState.MOVE, (64, 64))

    assert len(animation.frames) == 5
    assert repository.get("NW", AnimationState.MOVE, (64, 64)) is animation


def test_complete_game_demo_renders_dynamic_frames(tmp_path: Path):
    frames = render_game_demo(output_dir=tmp_path)

    assert len(frames) == len(_game_moves()) * FRAMES_PER_MOVE
    assert all(frame.exists() and frame.stat().st_size > 0 for frame in frames)

    first = Img().read(frames[0]).img
    last = Img().read(frames[-1]).img
    assert first.shape == last.shape
    assert np.any(first != last), "The final frame should reflect the completed moves."


def test_game_scene_draws_board_and_model_pieces():
    board = TextBoardParser.parse(
        [
            "bR bN bB bQ bK bB bN bR",
            "bP bP bP bP bP bP bP bP",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            ". . . . . . . .",
            "wP wP wP wP wP wP wP wP",
            "wR wN wB wQ wK wB wN wR",
        ]
    )
    scene = _create_scene(board)
    scene._board_renderer.draw()
    board_only = scene._canvas.canvas.img.copy()

    scene.draw()

    assert np.any(scene._canvas.canvas.img != board_only)
