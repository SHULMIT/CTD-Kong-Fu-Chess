from view.ui.scene.game_scene import GameScene
from view.ui.loop.game_loop import GameLoop
from collections.abc import Callable


class GameApplication:

    def __init__(
        self,
        scene: GameScene,
        on_close: Callable[[], None] | None = None,
    ):

        self._scene = scene
        self._running = True
        self._on_close = on_close or (lambda: None)

    def run(self) -> None:
        """Runs the interactive UI until the player closes it."""
        self._render()
        self._scene.bind_input()

        loop = GameLoop(
            update=self._update,
            render=self._render,
            is_running=lambda: self._running,
        )
        try:
            loop.run()
        finally:
            self._scene.canvas.close()
            self._on_close()

    def _update(self, _delta_time: float) -> None:
        key = self._scene.canvas.poll_events()
        self._running = (
            key != 27
            and self._scene.canvas.is_open()
            and not self._scene.should_close
        )
        # After game over, stop advancing the simulation —
        # just keep the GAME OVER screen visible.
        if self._scene.is_game_over:
            return
        self._scene.update(_delta_time)

    def _render(self) -> None:
        self._scene.draw()
        self._scene.canvas.present()
