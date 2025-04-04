from __future__ import annotations

from typing import TYPE_CHECKING

from potion.data_types.blend_mode import BlendMode
from potion.data_types.point import Point
from potion.data_types.vector2 import Vector2
from potion.renderer import Renderer
from potion.utilities import pmath

if TYPE_CHECKING:
    from potion.camera import Camera
    from potion.data_types.color import Color


class Line:
    """ A 2D line. """
    def __init__(self, a: Point, b: Point) -> None:
        self._a = Point(a.x, a.y)
        self._b = Point(b.x, b.y)

    def __str__(self) -> str:
        return f"Line({self.a}, {self.b})"

    def __repr__(self) -> str:
        return str(self)

    @property
    def a(self) -> Point:
        """ The first endpoint of the line. """
        return self._a

    @property
    def b(self) -> Point:
        """ The second endpoint of the line. """
        return self._b

    def nearest_point(self, point: Point) -> Point:
        """ Return a point on the line segment that is closest to a given point.
        https://stackoverflow.com/a/51240898
        """
        line_vector = (self.b - self.a).to_vector2()
        point_vector = (point - self.a).to_vector2()
        t = pmath.clamp(Vector2.dot_product(line_vector.normalized(), point_vector / line_vector.length()), 0, 1)
        nearest = line_vector * t + self.a.to_vector2()
        return Point(nearest.x, nearest.y)

    def draw(self, camera: Camera, color: Color) -> None:
        """ Draw the line. """
        a = camera.world_to_render_position(self.a)
        b = camera.world_to_render_position(self.b)
        line = Line(a, b)
        Renderer.set_render_draw_blend_mode(BlendMode.BLEND)
        Renderer.draw_line(line, color)
        Renderer.clear_render_draw_blend_mode()
