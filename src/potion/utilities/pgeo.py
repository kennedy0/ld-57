from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from potion.data_types.circle import Circle
    from potion.data_types.rect import Rect


def rect_intersects_rect(a: Rect, b: Rect) -> bool:
    """ Check if two rectangles intersect. """
    return b.left() <= a.right() and a.left() <= b.right() and b.top() <= a.bottom() and a.top() <= b.bottom()


def circle_intersects_circle(a: Circle, b: Circle) -> bool:
    """ Check if two circles intersect. """
    return a.center().distance_to_f(b.center()) <= a.radius + b.radius


def rect_intersects_circle(r: Rect, c: Circle) -> bool:
    """ Check if a rectangle intersects a circle.
    Logic and diagram: https://stackoverflow.com/a/43546279
    """
    # Check if the center point of the circle is inside the rectangle
    if r.contains_point(c.center()):
        return True

    # Check if any of the rectangle corners are inside the circle
    if c.contains(r.top_left()) or c.contains(r.top_right()) or c.contains(r.bottom_left()) or c.contains(r.bottom_right()):
        return True

    # Check if any of the rectangle edges intersect the circle
    distance_x = abs(c.x - r.center().x)
    distance_y = abs(c.y - r.center().y)
    if distance_x <= r.width / 2 and distance_y < r.height / 2 + c.radius:
        return True
    if distance_y <= r.height / 2 and distance_x < r.width / 2 + c.radius:
        return True

    # If none of the above conditions are met, there is no intersection
    return False
