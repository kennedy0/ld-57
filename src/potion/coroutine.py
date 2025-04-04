from __future__ import annotations

from typing import Generator, TYPE_CHECKING

from potion.log import Log
from potion.time import Time

if TYPE_CHECKING:
    from potion.entity import Entity


_coroutines: list[Generator] = []
_stop: list[Generator] = []


def start_coroutine(c: Generator) -> Generator | None:
    """ Start a coroutine. """
    # Make sure a generator was passed in
    if not isinstance(c, Generator):
        name = getattr(c, "__name__", str(c))
        Log.error(f"Cannot start coroutine: {name} is not a Generator")
        return

    # Add the generator to the list of coroutines
    global _coroutines
    _coroutines.append(c)
    return c


def stop_coroutine(c: Generator) -> None:
    """ Stop a coroutine. """
    # Make sure a generator was passed in
    if not isinstance(c, Generator):
        Log.error(f"Cannot stop coroutine: {c.__name__} is not a Generator")
        return

    # Make sure the coroutine is running
    if c not in _coroutines:
        Log.error(f"Cannot stop coroutine: {c.__name__} is not running")
        return

    # Add the coroutine to the stop list
    global _stop
    _stop.append(c)


def update_coroutines() -> None:
    """ Update the coroutines. """
    global _coroutines
    global _stop

    if not _coroutines:
        return

    # Stop coroutines
    for c in _stop:
        _coroutines.remove(c)
    _stop.clear()

    # Run coroutines
    remove = []
    for c in _coroutines:
        try:
            next(c)
        except StopIteration:
            remove.append(c)

    # Remove coroutines that have finished
    for c in remove[:]:
        _coroutines.remove(c)


def wait_for_frames(frames: int) -> Generator:
    """ Wait for a given amount of frames.
    Usage:
        `yield from wait_for_frames()`
    """
    f = 0
    while f < frames:
        f += 1
        yield


def wait_for_seconds(seconds: float) -> Generator:
    """ Wait for a given amount of seconds.
    Usage:
        `yield from wait_for_seconds()`
    """
    t = 0
    while t < seconds:
        t += Time.delta_time
        yield
