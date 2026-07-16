from config.constants import DEFAULT_BOARD_PATH
from board_io.board_loader import BoardLoader
from controller.controller import Controller
from game.game_engine import GameEngine
from model.piece import Piece
from model.position import Position
from realtime.duration_calculator import DurationCalculator
from realtime.real_time_arbiter import RealTimeArbiter
from rules.rule_engine import RuleEngine
from view.ui.scene.game_scene import GameScene


def _build_game():
    board = BoardLoader.load(DEFAULT_BOARD_PATH)
    game_engine = GameEngine(
        board=board,
        rule_engine=RuleEngine(),
        arbiter=RealTimeArbiter(board),
        duration_calculator=DurationCalculator(),
    )
    controller = Controller(game_engine)
    return board, game_engine, controller, GameScene(controller, game_engine)


def test_default_board_contains_a_full_starting_position():
    board = BoardLoader.load(DEFAULT_BOARD_PATH)

    pieces = [
        board.get_piece(Position(row, column))
        for row in range(board.height)
        for column in range(board.width)
    ]

    assert (board.height, board.width) == (8, 8)
    assert sum(isinstance(piece, Piece) for piece in pieces) == 32


def test_scene_update_advances_a_move_and_can_render_afterward():
    board, _engine, controller, scene = _build_game()
    source = Position(6, 0)
    target = Position(5, 0)
    pawn = board.get_piece(source)

    controller.handle_position(source)
    controller.handle_position(target)
    scene.update(1.0)
    scene.draw()

    assert board.get_piece(target) is pawn
    assert pawn.position == target


def test_scene_records_user_errors_as_temporary_status_messages():
    _board, _engine, _controller, scene = _build_game()

    scene._show_user_error("Illegal move")

    assert scene._status_message == "Illegal move"
    assert scene._status_message_expires_at > 0
