from __future__ import annotations

from typing import TYPE_CHECKING

from copy import deepcopy
from math import cos, sin, radians, sqrt

if TYPE_CHECKING:
    from potion.data_types.point import Point


class Vector2:
    """ A 2D vector. """
    def __init__(self, x: float, y: float) -> None:
        self._x = x
        self._y = y

    def __str__(self) -> str:
        return f"Vector2({self.x}, {self.y})"

    def __repr__(self) -> str:
        return str(self)

    def __bool__(self) -> bool:
        return bool(self._x or self._y)

    def __len__(self):
        return self.to_tuple().__len__()

    def __getitem__(self, item):
        return self.to_tuple().__getitem__(item)

    def __iter__(self):
        return iter(self.to_tuple())

    def __eq__(self, other: Point) -> bool:
        return self.x == other.x and self.y == other.y

    def __add__(self, other: Vector2) -> Vector2:
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vector2) -> Vector2:
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, other: Vector2 | float) -> Vector2:
        if isinstance(other, Vector2):
            return Vector2(self.x * other.x, self.y * other.y)
        else:
            return Vector2(self.x * other, self.y * other)

    def __truediv__(self, other: Vector2 | float) -> Vector2:
        if isinstance(other, Vector2):
            return Vector2(self.x / other.x, self.y / other.y)
        else:
            return Vector2(self.x / other, self.y / other)

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    @staticmethod
    def zero() -> Vector2:
        return Vector2(0, 0)

    @staticmethod
    def one() -> Vector2:
        return Vector2(1, 1)

    @staticmethod
    def up() -> Vector2:
        return Vector2(0, -1)

    @staticmethod
    def down() -> Vector2:
        return Vector2(0, 1)

    @staticmethod
    def left() -> Vector2:
        return Vector2(-1, 0)

    @staticmethod
    def right() -> Vector2:
        return Vector2(1, 0)

    @staticmethod
    def distance(a: Vector2, b: Vector2) -> float:
        """ Return the distance between two vectors. """
        return (b - a).length()

    @staticmethod
    def dot_product(a: Vector2, b: Vector2) -> float:
        """ Return the dot product of two vectors. """
        return a.x * b.x + a.y * b.y

    def length(self) -> float:
        """ The length of the vector. """
        return sqrt(self.x * self.x + self.y * self.y)

    def to_tuple(self) -> tuple[float, float]:
        """ Return a copy of the vector as a tuple. """
        return self.x, self.y

    def to_point(self) -> Point:
        """ Return a copy of the vector as a Point. """
        from potion.data_types.point import Point
        return Point(self.x, self.y)

    def copy(self) -> Vector2:
        """ Return a copy of the vector. """
        return deepcopy(self)

    def normalized(self) -> Vector2:
        """ Return a normalized copy of the vector. """
        x = self.x
        y = self.y

        if self.length() == 0:
            x = 0
            y = 0
        else:
            scale = 1 / self.length()
            x *= scale
            y *= scale
        return Vector2(x, y)

    def rotated(self, angle: float) -> Vector2:
        """ Return a copy of the vector, rotated clockwise.
        The `angle` argument is specified in degrees.
        """
        x = self.x * cos(radians(angle)) - self.y * sin(radians(angle))
        y = self.x * sin(radians(angle)) + self.y * cos(radians(angle))
        return Vector2(x, y)

    def distance_to(self, other: Vector2) -> float:
        """ Return the distance to another vector. """
        return self.distance(self, other)
