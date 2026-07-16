import cv2
from unittest.mock import patch

from board_io.board_loader import BoardLoader
from config.constants import DEFAULT_BOARD_PATH
from controller.controller import Controller
from errors.user_input_errors import ClickEmptySourceError
from game.game_engine import GameEngine
from model.position import Position
from realtime.duration_calculator import DurationCalculator
from realtime.real_time_arbiter import RealTimeArbiter
from rules.rule_engine import RuleEngine
from view.ui.input.ui_input_handler import UiInputHandler


class _ControllerSpy:
    def __init__(self) -> None:
        self.clicked_positions: list[Position] = []
        self.jumped_positions: list[Position] = []

    def handle_position(self, position: Position) -> None:
        self.clicked_positions.append(position)

    def jump_at(self, position: Position) -> None:
        self.jumped_positions.append(position)


class _LayoutStub:
    def is_inside_board(self, x: int, y: int) -> bool:
        return True

    def pixel_to_cell(self, x: int, y: int) -> Position:
        return Position(row=y, column=x)


class _ScalerStub:
    def to_canvas(self, x: int, y: int) -> tuple[int, int]:
        return x, y


def test_right_click_jumps_at_clicked_square():
    controller = _ControllerSpy()
    handler = UiInputHandler(
        layout=_LayoutStub(),
        controller=controller,
        scaler=_ScalerStub(),
        report_user_error=lambda _message: None,
    )

    handler.handle_mouse(
        cv2.EVENT_RBUTTONDOWN,
        3,
        2,
        0,
        None,
    )

    assert controller.jumped_positions == [Position(2, 3)]
    assert controller.clicked_positions == []


def test_left_click_keeps_normal_selection_and_move_behavior():
    controller = _ControllerSpy()
    handler = UiInputHandler(
        layout=_LayoutStub(),
        controller=controller,
        scaler=_ScalerStub(),
        report_user_error=lambda _message: None,
    )

    with patch(
        "view.ui.input.ui_input_handler.time.perf_counter",
        side_effect=[0.0, 0.3],
    ):
        handler.handle_mouse(cv2.EVENT_LBUTTONDOWN, 3, 2, 0, None)
        handler.update()

    assert controller.clicked_positions == [Position(2, 3)]
    assert controller.jumped_positions == []


def test_double_click_jumps_without_triggering_a_normal_click():
    controller = _ControllerSpy()
    handler = UiInputHandler(
        layout=_LayoutStub(),
        controller=controller,
        scaler=_ScalerStub(),
        report_user_error=lambda _message: None,
    )

    with patch(
        "view.ui.input.ui_input_handler.time.perf_counter",
        side_effect=[0.0, 0.1],
    ):
        handler.handle_mouse(cv2.EVENT_LBUTTONDOWN, 3, 2, 0, None)
        handler.handle_mouse(cv2.EVENT_LBUTTONDBLCLK, 3, 2, 0, None)

    assert controller.jumped_positions == [Position(2, 3)]
    assert controller.clicked_positions == []


class _ErrorController:
    def handle_position(self, position: Position) -> None:
        raise ClickEmptySourceError()


class _OutsideBoardLayout(_LayoutStub):
    def is_inside_board(self, x: int, y: int) -> bool:
        return False


def test_user_input_errors_are_reported_without_escaping_callback():
    messages: list[str] = []
    handler = UiInputHandler(
        layout=_LayoutStub(),
        controller=_ErrorController(),
        scaler=_ScalerStub(),
        report_user_error=messages.append,
    )

    with patch(
        "view.ui.input.ui_input_handler.time.perf_counter",
        side_effect=[0.0, 0.3],
    ):
        handler.handle_mouse(cv2.EVENT_LBUTTONDOWN, 3, 2, 0, None)
        handler.update()

    assert messages == ["ERROR CLICK EMPTY SOURCE"]


def test_click_outside_board_is_reported_to_the_user():
    messages: list[str] = []
    handler = UiInputHandler(
        layout=_OutsideBoardLayout(),
        controller=_ControllerSpy(),
        scaler=_ScalerStub(),
        report_user_error=messages.append,
    )

    handler.handle_mouse(cv2.EVENT_LBUTTONDOWN, 3, 2, 0, None)

    assert messages == ["ERROR CLICK OUTSIDE BOARD"]


def test_illegal_move_is_reported_without_stopping_input_flow():
    board = BoardLoader.load(DEFAULT_BOARD_PATH)
    engine = GameEngine(
        board=board,
        rule_engine=RuleEngine(),
        arbiter=RealTimeArbiter(board),
        duration_calculator=DurationCalculator(),
    )
    messages: list[str] = []
    handler = UiInputHandler(
        layout=_LayoutStub(),
        controller=Controller(engine),
        scaler=_ScalerStub(),
        report_user_error=messages.append,
    )

    with patch(
        "view.ui.input.ui_input_handler.time.perf_counter",
        side_effect=[0.0, 0.3, 0.4, 0.7],
    ):
        handler.handle_mouse(cv2.EVENT_LBUTTONDOWN, 0, 6, 0, None)
        handler.update()
        handler.handle_mouse(cv2.EVENT_LBUTTONDOWN, 1, 5, 0, None)
        handler.update()

    assert messages == ["Illegal move"]
    assert engine.get_motions() == ()
