from __future__ import annotations

from typing import TYPE_CHECKING

from potion.data_types.blend_mode import BlendMode
from potion.data_types.point import Point
from potion.data_types.rect import Rect
from potion.renderer import Renderer
from potion.utilities import pgeo


if TYPE_CHECKING:
    from potion.camera import Camera
    from potion.data_types.color import Color


class Circle:
    """ A 2D circle. """
    def __init__(self, x: int, y: int, radius: int) -> None:
        self._x = x
        self._y = y
        self._radius = radius

    def __str__(self) -> str:
        return f"Circle(x={self.x}, y={self.y}, radius={self.radius})"

    def __repr__(self) -> str:
        return str(self)

    @property
    def x(self) -> int:
        """ The X coordinate of the center of the circle. """
        return self._x

    @property
    def y(self) -> int:
        """ The Y coordinate of the center of the circle. """
        return self._y

    @property
    def radius(self) -> int:
        """ The radius of the circle. """
        return self._radius

    def diameter(self) -> int:
        """ The diameter of the circle. """
        return self.radius * 2 + 1

    def top(self) -> int:
        """ The Y position of the top edge of the circle. """
        return self.y - self.radius

    def bottom(self) -> int:
        """ The Y position of the bottom edge of the circle. """
        return self.rect().bottom()

    def left(self) -> int:
        """ The X position of the left edge of the circle. """
        return self.x - self.radius

    def right(self) -> int:
        """ The X position of the right edge of the circle. """
        return self.rect().right()

    def center(self) -> Point:
        """ The center point of the circle. """
        return Point(self.x, self.y)

    def rect(self) -> Rect:
        """ The bounding box for the circle  """
        return Rect(self.left(), self.top(), self.diameter(), self.diameter())

    def contains(self, point: Point) -> bool:
        """ Check if a point is inside the circle. """
        return self.center().distance_to(point) <= self.radius

    def intersects_circle(self, circle: Circle) -> bool:
        """ Check if this circle intersects another. """
        return pgeo.circle_intersects_circle(self, circle)

    def intersects_rect(self, rect: Rect) -> bool:
        """ Check if this circle intersects a rectangle. """
        return pgeo.rect_intersects_circle(rect, self)

    def draw(self, camera: Camera, color: Color, solid: bool = False) -> None:
        """ Draw the circle. """
        center = camera.world_to_render_position(self.center())
        circle = Circle(center.x, center.y, self.radius)

        Renderer.set_render_draw_blend_mode(BlendMode.BLEND)
        if solid:
            Renderer.draw_circle_solid(circle, color)
        else:
            Renderer.draw_circle_outline(circle, color)
        Renderer.clear_render_draw_blend_mode()
