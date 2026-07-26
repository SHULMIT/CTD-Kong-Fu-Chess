"""Immutable commands accepted at the external game boundary."""

from dataclasses import dataclass

from model.position import Position


@dataclass(frozen=True)
class MoveCommand:
    """Requests movement from one board position to another.

    מייצגת בקשה להזיז כלי מעמדת מקור לעמדת יעד.

    Responsibility: Requests movement from one board position to another.

    אחריות: מייצגת בקשה להזיז כלי מעמדת מקור לעמדת יעד."""

    source: Position
    target: Position


@dataclass(frozen=True)
class JumpCommand:
    """Requests a jump for the piece at a board position.

    מייצגת בקשה להקפיץ את הכלי הנמצא בעמדה נתונה.

    Responsibility: Requests a jump for the piece at a board position.

    אחריות: מייצגת בקשה להקפיץ את הכלי הנמצא בעמדה נתונה."""

    position: Position


@dataclass(frozen=True)
class LegalMovesCommand:
    """Requests legal destinations for the piece at a board position.

    מייצגת בקשה לקבל את היעדים החוקיים של כלי בעמדה נתונה.

    Responsibility: Requests legal destinations for the piece at a board position.

    אחריות: מייצגת בקשה לקבל את היעדים החוקיים של כלי בעמדה נתונה."""

    position: Position


NetworkCommand = MoveCommand | JumpCommand | LegalMovesCommand
