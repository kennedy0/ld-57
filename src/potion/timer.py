from potion.log import Log
from potion.time import Time


class Timer:
    """ A timer that starts at 0 and counts up to its duration (in seconds).

    A fixed interval based on the engine framerate is used to increment the value rather than Time.delta_time.
    This keeps the timer running lockstep with each frame, rather than causing variable, unpredictable results.
    """
    def __init__(self, duration: float = 1) -> None:
        self._value = 0
        self._duration = 1
        self._running = False
        self._finished = False
        self._loop = True
        self._delta = Time.frames_to_s(1)

        self.set_duration(duration)

    @property
    def value(self) -> float:
        """ The current value of the timer. """
        return self._value

    @property
    def duration(self) -> float:
        """ The duration of the timer. """
        return self._duration

    @property
    def running(self) -> bool:
        """ If True, the timer is running. """
        return self._running

    @property
    def finished(self) -> bool:
        """ If True, the timer has reached its duration this frame. """
        return self._finished

    @property
    def loop(self) -> bool:
        """ If True, the timer will loop when it finishes. """
        return self._loop

    @loop.setter
    def loop(self, value: bool) -> None:
        self._loop = value

    def set_duration(self, duration: float) -> None:
        """ Set the timer's duration. """
        if duration <= 0:
            Log.error("Timer duration must be greater than 0.")
            return

        self._duration = duration

    def start(self) -> None:
        """ Start the timer. """
        if self._duration <= 0:
            Log.error("Timer duration must be greater than 0 to start")
            return

        self._running = True

    def update(self) -> None:
        """ Update the timer. """
        self._finished = False
        if not self._running:
            return

        self._value += self._delta
        if self._value >= self.duration:
            self._finished = True
            if self._loop:
                self._value -= self.duration
            else:
                self._value = self.duration

    def pause(self) -> None:
        """ Pause the timer. """
        self._running = False

    def stop(self) -> None:
        """ Stop the timer and set its value back to zero. """
        self._value = 0
        self._running = False
        self._finished = False

    def reset(self) -> None:
        """ Reset the timer. """
        self._value = 0
        self._finished = False

    def progress(self) -> float:
        """ Get the progress of the timer as a 0-1 float value. """
        if self._finished:
            return 1.0

        return self._value / self._duration
