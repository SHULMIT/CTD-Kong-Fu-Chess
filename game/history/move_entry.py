from dataclasses import dataclass


@dataclass(slots=True)
class MoveEntry:
    """
    Represents a single move displayed in the UI.
    """

    time: float
    player: str
    piece: str
    source: str
    target: str

