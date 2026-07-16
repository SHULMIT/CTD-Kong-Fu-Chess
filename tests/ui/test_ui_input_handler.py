import cv2

from errors.user_input_errors import ClickEmptySourceError
from model.position import Position
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

    handler.handle_mouse(
        cv2.EVENT_LBUTTONDOWN,
        3,
        2,
        0,
        None,
    )

    assert controller.clicked_positions == [Position(2, 3)]
    assert controller.jumped_positions == []


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

    handler.handle_mouse(cv2.EVENT_LBUTTONDOWN, 3, 2, 0, None)

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
