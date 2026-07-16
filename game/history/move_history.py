"""
move_history.py

Stores the move history displayed by the UI.

Responsibilities:
    - Store executed moves.
    - Provide access to the move history.
"""
from game.history.move_entry import MoveEntry
class MoveHistory(list[MoveEntry]):
    """
    Stores the chronological move history.
    """

    def add(
        self,
        entry: MoveEntry,
    ) -> None:

        self.append(entry)

    def clear_history(self) -> None:

        self.clear()    