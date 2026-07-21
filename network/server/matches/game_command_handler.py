"""Authorization and execution of parsed multiplayer game commands."""

from errors.user_input_errors import UserInputError
from game.game_engine import GameEngine
from model.piece import Piece
from model.position import Position
from network.server.transport.client_messenger import ClientMessenger
from network.server.transport.commands import JumpCommand, LegalMovesCommand, MoveCommand, NetworkCommand
from network.server.transport.game_snapshot_serializer import JsonValue
from network.server.matches.session_manager import SessionManager


class GameCommandHandler:
    """Executes parsed commands through the authoritative game API."""

    def __init__(self, game_engine: GameEngine, sessions: SessionManager) -> None:
        self._game_engine = game_engine
        self._sessions = sessions

    def execute(
        self,
        connection: object,
        command: NetworkCommand,
    ) -> dict[str, JsonValue]:
        """Authorize ownership and return the existing protocol response."""
        if self._game_engine.game_over:
            return ClientMessenger.rejection("game_over")
        position = command.source if isinstance(command, MoveCommand) else command.position
        piece = self._controlled_piece(connection, position)
        if isinstance(piece, str):
            return ClientMessenger.rejection(piece)
        if isinstance(command, LegalMovesCommand):
            legal_moves = self._game_engine.get_legal_moves(command.position)
            return {
                "type": "legal_moves",
                "source": self.serialize_position(command.position),
                "positions": [
                    self.serialize_position(item)
                    for item in sorted(legal_moves, key=lambda item: (item.row, item.column))
                ],
            }
        if isinstance(command, MoveCommand):
            result = self._game_engine.request_move(command.source, command.target)
            if not result.is_accepted:
                return ClientMessenger.rejection(result.reason.value)
            return {"type": "command_accepted", "command": "move"}
        try:
            self._game_engine.jump(command.position)
        except UserInputError:
            return ClientMessenger.rejection("illegal_jump")
        return {"type": "command_accepted", "command": "jump"}

    def _controlled_piece(self, connection: object, position: Position) -> Piece | str:
        if not self._game_engine.is_inside(position):
            return "missing_piece"
        piece = self._game_engine.get_piece(position)
        if not isinstance(piece, Piece):
            return "missing_piece"
        if not self._sessions.can_control(connection, piece.color):
            return "not_your_piece"
        return piece

    @staticmethod
    def serialize_position(position: Position) -> dict[str, JsonValue]:
        return {"row": position.row, "column": position.column}
