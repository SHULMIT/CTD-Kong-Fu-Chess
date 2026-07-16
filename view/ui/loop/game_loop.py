import time
from typing import Callable


class GameLoop:
    """
    Runs the main game loop.
    """

    TARGET_FPS = 60

    def __init__(
        self,
        update: Callable[[float], None],
        render: Callable[[], None],
        is_running: Callable[[], bool],
    ):

        self._update = update
        self._render = render
        self._is_running = is_running

    def run(self) -> None:
        """
        Starts the game loop.
        """

        previous_time = time.perf_counter()

        while self._is_running():

            current_time = time.perf_counter()

            delta_time = current_time - previous_time

            previous_time = current_time

            self._update(delta_time)

            self._render()

            elapsed = time.perf_counter() - current_time

            target_frame = 1 / self.TARGET_FPS

            if elapsed < target_frame:

                time.sleep(target_frame - elapsed)