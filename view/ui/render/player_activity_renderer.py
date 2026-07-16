"""Renders player scores and recent actions beside the board."""

import cv2

from game.player_activity_service import PlayerAction, PlayerActivityService
from model.piece import PieceColor
from view.ui.layout.board_layout import BoardLayout
from view.ui.window.game_canvas import GameCanvas


class PlayerActivityRenderer:
    """Draws one compact activity panel for each player."""

    def __init__(
        self,
        canvas: GameCanvas,
        layout: BoardLayout,
        player_activity: PlayerActivityService,
    ) -> None:
        self._canvas = canvas
        self._layout = layout
        self._player_activity = player_activity

    def draw(self) -> None:
        """Draws the white and black player panels."""

        self._draw_panel(
            player=PieceColor.WHITE,
            x=16,
            width=self._layout.board_x - 32,
            title="WHITE",
        )
        self._draw_panel(
            player=PieceColor.BLACK,
            x=self._layout.board_x + self._layout.board_size + 16,
            width=(
                self._canvas.width
                - self._layout.board_x
                - self._layout.board_size
                - 32
            ),
            title="BLACK",
        )

    def _draw_panel(
        self,
        player: PieceColor,
        x: int,
        width: int,
        title: str,
    ) -> None:
        if width < 120:
            return

        image = self._canvas.canvas.img
        y = self._layout.cells_y
        height = self._layout.inner_board_size
        overlay = image.copy()
        cv2.rectangle(
            overlay,
            (x, y),
            (x + width, y + height),
            (25, 25, 25),
            -1,
        )
        cv2.addWeighted(overlay, 0.78, image, 0.22, 0, image)

        padding = 18
        font = cv2.FONT_HERSHEY_DUPLEX
        header_scale = 2.34
        body_scale = 1.74
        text_x = x + padding
        text_y = y + 70
        score = self._player_activity.get_score(player)
        header_color = (230, 230, 230)

        cv2.putText(
            image,
            title,
            (text_x, text_y),
            font,
            header_scale,
            header_color,
            3,
            cv2.LINE_AA,
        )
        cv2.putText(
            image,
            f"Score: {score}",
            (text_x, text_y + 80),
            font,
            body_scale,
            (0, 215, 255),
            2,
            cv2.LINE_AA,
        )

        actions = self._player_activity.get_actions(player)
        for index, action in enumerate(actions):
            line_y = text_y + 190 + index * 120
            self._draw_action(
                action=action,
                x=text_x,
                y=line_y,
                max_width=width - padding * 2,
            )

    def _draw_action(
        self,
        action: PlayerAction,
        x: int,
        y: int,
        max_width: int,
    ) -> None:
        image = self._canvas.canvas.img
        timestamp = self._format_time(action.timestamp_milliseconds)
        text = f"{timestamp}  {action.description}"
        text = self._truncate(text, max_width)

        cv2.putText(
            image,
            text,
            (x, y),
            cv2.FONT_HERSHEY_DUPLEX,
            1.56,
            (245, 245, 245),
            2,
            cv2.LINE_AA,
        )

    @staticmethod
    def _format_time(milliseconds: int) -> str:
        minutes, remainder = divmod(milliseconds, 60_000)
        seconds, remainder = divmod(remainder, 1_000)
        return f"{minutes:02}:{seconds:02}.{remainder:03}"

    @staticmethod
    def _truncate(text: str, max_width: int) -> str:
        font = cv2.FONT_HERSHEY_DUPLEX
        scale = 1.56
        while text and cv2.getTextSize(text, font, scale, 1)[0][0] > max_width:
            text = f"{text[:-4]}..."
        return text
