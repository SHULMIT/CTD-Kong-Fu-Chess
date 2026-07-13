class Clock:
    def __init__(self):
        self._time_ms = 0

    @property
    def current_time(self):
        return self._time_ms

    def tick(self, ms):
        if ms < 0:
            raise ValueError("Time cannot go backwards")
        self._time_ms += ms