import random


def sign(n: int | float) -> int:
    """ Return the sign of a number. """
    if n < 0:
        return -1
    else:
        return 1


def clamp(value: float, min_value: float, max_value: float) -> int | float:
    """ Returns the value clamped to the inclusive range of min and max. """
    return max(min_value, min(value, max_value))


def remap(value: float, old_min: float, old_max: float, new_min: float, new_max: float) -> float:
    """ Remaps a number from one range to another. """
    if old_min == old_max:
        return new_min

    return (value - old_min) * (new_max - new_min) / (old_max - old_min) + new_min


def lerp(a: float, b: float, t: float) -> float:
    """ Linearly interpolates between a and b, by value t.
    When t = 0, returns a
    When t = 1, returns b
    When t = 0.5, returns the midpoint of and b.
    """
    value = a * (1 - t) + b * t
    return clamp(value, min(a, b), max(a, b))


def snap_to_interval(value: float, interval: int) -> int:
    """ Snap a number to the nearest interval. """
    return round(value / float(interval)) * interval


def random_bool() -> bool:
    """ Returns a random boolean value. """
    return bool(random.getrandbits(1))


def smooth_step(a: float, b: float, t: float) -> float:
    """ Interpolate between two values with smoothing at the limits. """
    t = clamp(t, 0, 1)
    t = -2 * t * t * t + 3 * t * t
    return b * t + a * (1 - t)
