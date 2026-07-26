"""Connection membership and piece-color ownership for one local game."""

from model.piece import PieceColor


class SessionManager:
    """Assigns the two available colors to independent client identities.

    מקצה את שני הצבעים הזמינים לזהויות לקוח נפרדות.

    Responsibility: Assigns the two available colors to independent client identities.

    אחריות: מקצה את שני הצבעים הזמינים לזהויות לקוח נפרדות."""

    _COLOR_ORDER = (PieceColor.WHITE, PieceColor.BLACK)

    def __init__(self) -> None:
        """Initialize the instance and its dependencies.

        מאתחלת את המופע ואת התלויות שלו."""
        self._colors_by_client: dict[object, PieceColor] = {}

    def connect(self, client: object) -> PieceColor | None:
        """Assign an available color, or return ``None`` when the game is full.

        מקצה צבע פנוי או מחזירה ``None`` כאשר המשחק מלא."""
        existing_color = self._colors_by_client.get(client)
        if existing_color is not None:
            return existing_color

        assigned_colors = set(self._colors_by_client.values())
        for color in self._COLOR_ORDER:
            if color not in assigned_colors:
                self._colors_by_client[client] = color
                return color
        return None

    def assign(self, client: object, color: PieceColor) -> bool:
        """Assign a chosen color when matchmaking creates a game.

        מקצה צבע שנבחר מראש כאשר matchmaking יוצר משחק."""
        existing = self._colors_by_client.get(client)
        if existing is not None:
            return existing is color
        if color in self._colors_by_client.values():
            return False
        self._colors_by_client[client] = color
        return True

    def disconnect(self, client: object) -> None:
        """Release the color assigned to a disconnected client.

        משחררת את הצבע שהוקצה ללקוח שהתנתק."""
        self._colors_by_client.pop(client, None)

    def color_for(self, client: object) -> PieceColor | None:
        """Return the client's assigned color, if connected.

        מחזירה את הצבע שהוקצה ללקוח, אם הוא מחובר למשחק."""
        return self._colors_by_client.get(client)

    def can_control(self, client: object, piece_color: PieceColor) -> bool:
        """Return whether the client owns pieces of ``piece_color``.

        מחזירה האם ללקוח יש בעלות על כלים בצבע ``piece_color``."""
        return self.color_for(client) is piece_color

    @property
    def clients(self) -> tuple[object, ...]:
        """Return an immutable snapshot of accepted client identities.

        מחזירה תמונת מצב בלתי־ניתנת לשינוי של זהויות הלקוחות שהתקבלו."""
        return tuple(self._colors_by_client)
