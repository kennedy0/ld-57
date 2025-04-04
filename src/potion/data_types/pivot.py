from potion.log import Log


class Pivot:
    """ Represents a pivot point inside a rectangle.
    The X and Y values are always between 0 and 1.

       0    X    1
    0  +----+----+
       |    |    |
    Y  +----+----+
       |    |    |
    1  +----+----+
    """
    def __init__(self) -> None:
        self._x = 0
        self._y = 0

    def __str__(self) -> str:
        return f"Pivot(x={self._x}, y={self.y})"

    def __repr__(self) -> str:
        return str(self)

    @property
    def x(self) -> float:
        """ The X value for the pivot. """
        return self._x

    @x.setter
    def x(self, value: float) -> None:
        if value < 0 or value > 1:
            Log.error(f"Pivot point X must be in range 0 to 1: {value}")
            return
        self._x = value

    @property
    def y(self) -> float:
        """ The Y value for the pivot. """
        return self._y

    @y.setter
    def y(self, value: float) -> None:
        if value < 0 or value > 1:
            Log.error(f"Pivot point Y must be in range 0 to 1: {value}")
            return
        self._y = value

    def set_top_left(self) -> None:
        self.x = 0
        self.y = 0

    def set_top_center(self) -> None:
        self.x = 0.5
        self.y = 0

    def set_top_right(self) -> None:
        self.x = 1
        self.y = 0

    def set_center_left(self) -> None:
        self.x = 0
        self.y = 0.5

    def set_center(self) -> None:
        self.x = 0.5
        self.y = 0.5

    def set_center_right(self) -> None:
        self.x = 1
        self.y = 0.5

    def set_bottom_left(self) -> None:
        self.x = 0
        self.y = 1

    def set_bottom_center(self) -> None:
        self.x = 0.5
        self.y = 1

    def set_bottom_right(self) -> None:
        self.x = 1
        self.y = 1
