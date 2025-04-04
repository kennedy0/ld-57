from math import floor

from potion.camera import Camera
from potion.data_types.point import Point
from potion.data_types.rect import Rect
from potion.entity import Entity
from potion.sprite import Sprite


class LDtkSimplifiedIntGridEntity(Entity):
    """ An LDtk IntGrid layer from a 'Super Simple Export'. """
    def __init__(self) -> None:
        super().__init__()
        self.tags.add("ldtk")
        self.tags.add("ldtk_int_grid")
        self.grid_size = 0
        self.cells: dict[tuple[int, int], int] = {}
        self.sprite = Sprite.empty()

    def world_to_cell_position(self, position: Point) -> tuple[int, int]:
        """ Get the cell coordinates from a world position. """
        return (
            floor((position.x - self.x) / self.grid_size),
            floor((position.y - self.y) / self.grid_size)
        )

    def cell_to_world_position(self, cx: int, cy: int) -> Point:
        """ Get the world position of a cell.
        The position is the top-left corner of the cell.
        """
        return Point(
            self.x + (cx * self.grid_size),
            self.y + (cy * self.grid_size)
        )

    def cell_rect(self, cx: int, cy: int) -> Rect:
        """ Get the rect for a cell. """
        position = self.cell_to_world_position(cx, cy)
        return Rect(position.x, position.y, self.grid_size, self.grid_size)

    def get_value(self, cx: int, cy: int) -> int:
        """ Get a value from the grid.
        If the cell has no value, it will return 0.
        """
        return self.cells.get((cx, cy), 0)

    def set_value(self, cx: int, cy: int, value: int) -> None:
        """ Set a value on the grid. """
        self.cells[(cx, cy)] = value

    def draw(self, camera: Camera) -> None:
        self.sprite.draw(camera, self.position())

    def intersects(self, rect: Rect) -> bool:
        """ A rect intersects the int grid if its bounding box overlaps a cell with a value. """
        for point in (rect.top_left(), rect.top_right(), rect.bottom_left(), rect.bottom_right()):
            cx, cy = self.world_to_cell_position(point)
            if self.get_value(cx, cy):
                return True

        return False
