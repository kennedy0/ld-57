from __future__ import annotations

from copy import deepcopy
from math import floor, sqrt
from typing import TYPE_CHECKING

import sdl2

from potion.data_types.blend_mode import BlendMode
from potion.renderer import Renderer

if TYPE_CHECKING:
    from potion.camera import Camera
    from potion.data_types.color import Color
    from potion.data_types.vector2 import Vector2


class Point:
    """ A 2D point. """
    def __init__(self, x: float, y: float) -> None:
        self._x = floor(x)
        self._y = floor(y)

    def __str__(self) -> str:
        return f"Point({self.x}, {self.y})"

    def __repr__(self) -> str:
        return str(self)

    def __len__(self):
        return self.to_tuple().__len__()

    def __getitem__(self, item):
        return self.to_tuple().__getitem__(item)

    def __iter__(self):
        return iter(self.to_tuple())

    def __eq__(self, other: Point) -> bool:
        return self.x == other.x and self.y == other.y

    def __add__(self, other: Point) -> Point:
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Point) -> Point:
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, other: Point | float) -> Point:
        if isinstance(other, Point):
            return Point(self.x * other.x, self.y * other.y)
        else:
            return Point(self.x * other, self.y * other)

    def __truediv__(self, other: Point | float) -> Point:
        if isinstance(other, Point):
            return Point(self.x / other.x, self.y / other.y)
        else:
            return Point(self.x / other, self.y / other)

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    @staticmethod
    def zero() -> Point:
        return Point(0, 0)

    @staticmethod
    def one() -> Point:
        return Point(1, 1)

    @staticmethod
    def up() -> Point:
        return Point(0, -1)

    @staticmethod
    def down() -> Point:
        return Point(0, 1)

    @staticmethod
    def left() -> Point:
        return Point(-1, 0)

    @staticmethod
    def right() -> Point:
        return Point(1, 0)

    @staticmethod
    def distance(a: Point, b: Point) -> int:
        """ Return the distance between 2 points. """
        p = b - a
        return round(sqrt(p.x * p.x + p.y * p.y))

    @staticmethod
    def distance_f(a: Point, b: Point) -> float:
        """ Return the distance between 2 points. """
        p = b - a
        return sqrt(p.x * p.x + p.y * p.y)

    def copy(self) -> Point:
        """ Return a copy of the point. """
        return deepcopy(self)

    def to_tuple(self) -> tuple[int, int]:
        """ Return a copy of the point as a tuple. """
        return self.x, self.y

    def to_vector2(self) -> Vector2:
        """ Return a copy of this point as a Vector2. """
        from potion.data_types.vector2 import Vector2
        return Vector2(self.x, self.y)

    def to_sdl_point(self) -> sdl2.SDL_Point:
        """ Return a copy of the point as an SDL_Point. """
        return sdl2.SDL_Point(self.x, self.y)

    def distance_to(self, other: Point) -> int:
        """ Return the distance to another point. """
        return self.distance(self, other)

    def distance_to_f(self, other: Point) -> float:
        """ Return the distance to another point. """
        return self.distance_f(self, other)

    def draw(self, camera: Camera, color: Color) -> None:
        """ Draw the point. """
        Renderer.set_render_draw_blend_mode(BlendMode.BLEND)
        Renderer.draw_point(camera.world_to_render_position(self), color)
        Renderer.clear_render_draw_blend_mode()
