"""Tests for translating existing UI gestures into network commands."""

from unittest.mock import MagicMock

from model.piece import Piece, PieceColor, PieceType
from model.position import Position
from network.multiplayer_controller import MultiplayerController


def test_two_selected_positions_send_move_without_local_execution() -> None:
    source = Position(6, 0)
    target = Position(5, 0)
    game_state = MagicMock()
    game_state.is_inside.return_value = True
    game_state.has_piece.return_value = True
    game_state.get_piece.side_effect = [
        Piece(1, PieceType.PAWN, PieceColor.WHITE, source),
        Piece(1, PieceType.PAWN, PieceColor.WHITE, source),
        None,
    ]
    client = MagicMock()
    controller = MultiplayerController(game_state, client)

    controller.handle_position(source)
    client.request_legal_moves.assert_called_once_with(source)
    controller.handle_position(target)

    client.send_move.assert_called_once_with(source, target)
    assert controller.selected_position is None
    assert game_state.clear_legal_moves.call_count == 2


def test_jump_is_sent_without_modifying_remote_state() -> None:
    position = Position(6, 0)
    game_state = MagicMock()
    client = MagicMock()
    controller = MultiplayerController(game_state, client)

    controller.jump_at(position)

    client.send_jump.assert_called_once_with(position)
    game_state.jump.assert_not_called()


def test_deselect_clears_green_destination_markers() -> None:
    game_state = MagicMock()
    client = MagicMock()
    controller = MultiplayerController(game_state, client)

    controller.deselect()

    game_state.clear_legal_moves.assert_called_once_with()


def test_snapshot_replacing_selected_piece_clears_selection() -> None:
    source = Position(6, 0)
    original_piece = Piece(1, PieceType.PAWN, PieceColor.WHITE, source)
    replacement_piece = Piece(2, PieceType.PAWN, PieceColor.WHITE, source)
    game_state = MagicMock()
    game_state.is_inside.return_value = True
    game_state.has_piece.return_value = True
    game_state.get_piece.side_effect = [original_piece, replacement_piece]
    client = MagicMock(assigned_color=PieceColor.WHITE)
    controller = MultiplayerController(game_state, client)
    controller.handle_position(source)

    assert controller.selected_position is None
    game_state.clear_legal_moves.assert_called()
