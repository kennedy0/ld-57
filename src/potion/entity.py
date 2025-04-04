from __future__ import annotations

from math import floor
from typing import Iterator, Self, TYPE_CHECKING

from ulid import ULID

from potion.data_types.point import Point
from potion.data_types.rect import Rect
from potion.engine import Engine
from potion.log import Log
from potion.mouse import Mouse
from potion.utilities import pmath

if TYPE_CHECKING:
    from potion.level import Level
    from potion.scene import Scene
    from potion.camera import Camera


class Entity:
    """ Base entity class. """
    def __init__(self) -> None:
        self._scene = None
        self._level = None
        self._name = f"{self.__class__.__name__}-{ULID()}"
        self._tags = set()
        self._active = True
        self._pausable = True

        # Position
        self._x = 0
        self._y = 0

        # X and Y remainders
        # This is a float value that keeps track of fractional position.
        # Allows position adjustments of < 1 pixel to accumulate
        self._xr = 0.0
        self._yr = 0.0

        # Z (depth)
        self._z = 0

        # Collision
        self._collisions_enabled = False
        self._mouse_collisions_enabled = False

        self._solid = False

        self._width = 0
        self._height = 0

        self._collisions_this_frame: set[Entity] = set()
        self._collisions_last_frame: set[Entity] = set()
        self._mouse_this_frame = False
        self._mouse_last_frame = False

        # Arbitrary metadata
        self.metadata = {}

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"

    def __repr__(self) -> str:
        return str(self)

    @property
    def scene(self) -> Scene | None:
        """ The scene that the entity belongs to. """
        return self._scene

    @property
    def level(self) -> Level | None:
        """ The level that the entity belongs to. """
        return self._level

    @property
    def name(self) -> str:
        """ The name of the entity. """
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if value == self._name:
            return

        if self.scene:
            if self.scene.entities.rename(self._name, value):
                self._name = value
        else:
            self._name = value

    @property
    def tags(self) -> set[str]:
        """ A list of arbitrary tags on the entity. """
        return self._tags

    @property
    def active(self) -> bool:
        """ If True, the entity will be included in the update and draw loops. """
        return self._active

    @active.setter
    def active(self, value: bool) -> None:
        if self.scene:
            if value:
                self.scene.entities.set_active(self)
            else:
                self.scene.entities.set_inactive(self)

    @property
    def pausable(self) -> bool:
        """ If True, the update loop will not be run on the entity when the scene is paused. """
        return self._pausable

    @pausable.setter
    def pausable(self, value: bool) -> None:
        self._pausable = value

    @property
    def x(self) -> int:
        """ The X position of the entity. """
        return self._x

    @x.setter
    def x(self, value: int | float) -> None:
        self._x = floor(value)

    @property
    def y(self) -> int:
        """ The Y position of the entity. """
        return self._y

    @y.setter
    def y(self, value: int | float) -> None:
        self._y = floor(value)

    @property
    def z(self) -> int:
        """ The Z position determines the order that the entity is drawn.
        Higher (positive) numbers are drawn in the background; lower (negative) numbers are drawn in the foreground.
        """
        return self._z

    @z.setter
    def z(self, value: int) -> None:
        if value != self._z:
            if self.scene:
                self.scene.entities.flag_entity_draw_list_needs_sorting()
            self._z = value

    @property
    def collisions_enabled(self) -> bool:
        """ If true, the entity will be checked for collisions against other entities. """
        return self._collisions_enabled

    @collisions_enabled.setter
    def collisions_enabled(self, value: bool) -> None:
        self._collisions_enabled = value

    @property
    def mouse_collisions_enabled(self) -> bool:
        """ If true, the entity will be checked for mouse collision. """
        return self._mouse_collisions_enabled

    @mouse_collisions_enabled.setter
    def mouse_collisions_enabled(self, value: bool) -> None:
        self._mouse_collisions_enabled = value

    @property
    def solid(self) -> bool:
        """ If True, the entity is considered solid when colliding with other entities. """
        return self._solid

    @solid.setter
    def solid(self, value: bool) -> None:
        self._solid = value

    @property
    def width(self) -> int:
        """ The width of the entity (for collision). """
        return self._width

    @width.setter
    def width(self, value: int | float) -> None:
        self._width = floor(value)

    @property
    def height(self) -> int:
        """ The height of the entity (for collision). """
        return self._height

    @height.setter
    def height(self, value: int | float) -> None:
        self._height = floor(value)

    @classmethod
    def instantiate(cls) -> Self:
        """ Create an instance of this entity and add it to the current scene. """
        e = cls()

        if scene := Engine.scene():
            scene.entities.add(e)
        else:
            Log.error(f"Error instantiating {cls.__name__}; there is no scene loaded")

        return e

    def position(self) -> Point:
        """ The position of the entity. """
        return Point(self._x, self._y)

    def set_position(self, position: Point) -> None:
        """ Set the position of the entity. """
        self.x = position.x
        self.y = position.y

    def bbox(self) -> Rect:
        """ Get the bounding box of the entity. """
        return Rect(self.x, self.y, self.width, self.height)

    # Main game loop

    def awake(self) -> None:
        """ Called after the entity is created.
        Use this to initialize values, and set up references between entities.
        """
        pass

    def on_activate(self) -> None:
        """ Called when this entity is active, or added to the scene. """
        pass

    def start(self) -> None:
        """ This runs after awake, just before the first update.
        Use this to pass information back and forth between entities.
        """
        pass

    def update(self) -> None:
        """ Update loop. """
        pass

    def draw(self, camera: Camera) -> None:
        """ Draw loop. """
        pass

    def debug_draw(self, camera: Camera) -> None:
        """ If the engine is in debug mode, this will be called after the draw loop.
        This can be used to draw extra information about the entity for debugging purposes.
        """
        pass

    def on_deactivate(self) -> None:
        """ Called when this entity is deactivated, removed from the scene, or when the scene ends. """
        pass

    def end(self) -> None:
        """ Called immediately before the entity is removed from the scene, or when the scene ends. """
        pass

    def destroy(self) -> None:
        """ Remove this entity from the scene. """
        self.scene.entities.remove(self)

    # Collision callbacks

    def on_collision_begin(self, other: Entity) -> None:
        """ Called the first frame when a collision occurs between this entity and another entity. """
        pass

    def on_collision_stay(self, other: Entity) -> None:
        """ Called each frame a collision occurs between this entity and another entity.
        This is only called if the entities were colliding the previous frame and are still colliding this frame.
        """
        pass

    def on_collision_end(self, other: Entity) -> None:
        """ Called the first frame when a collision is no longer occurring between this entity and another entity. """
        pass

    def on_mouse_enter(self) -> None:
        """ Called the first frame the mouse hovers over the entity. """
        pass

    def on_mouse_over(self) -> None:
        """ Called every frame the mouse is over the entity. """
        pass

    def on_mouse_exit(self) -> None:
        """ Called the frame when the mouse stops hovering over the entity. """
        pass

    def intersects(self, rect: Rect) -> bool:
        """ Check if the entity intersects a given rect.
        Default behavior is to check against the entity's bounding box.
        More complex entities, such as a tilemap with collisions, may override this.
        """
        return self.bbox().intersects_rect(rect)

    # Utility functions

    def find(self, entity_name: str) -> Entity | None:
        """ Find an entity in the current scene. """
        return self.scene.entities.get(entity_name)

    def move_x(self, amount: float) -> None:
        """ Move the entity on the X-axis with collision. """
        # Get the movement amount
        x, xr = divmod(amount + self._xr, 1)
        move = int(x)
        self._xr = xr

        # Determine the movement direction
        direction = pmath.sign(move)

        while move != 0:
            new_x = self.x + direction

            # Solid collisions
            if self._invoke_solid_collisions(new_x, self.y):
                self._xr = 0
                break

            # Move
            self.x = new_x
            move -= direction

            # Non-solid collisions
            self._invoke_non_solid_collisions(self.x, self.y)

    def move_y(self, amount: float) -> None:
        """ Move the entity on the Y-axis with collision. """
        # Get the movement amount
        y, yr = divmod(amount + self._yr, 1)
        move = int(y)
        self._yr = yr

        # Determine the movement direction
        direction = pmath.sign(move)

        while move != 0:
            new_y = self.y + direction

            # Solid collisions
            if self._invoke_solid_collisions(self.x, new_y):
                self._yr = 0
                break

            # Move
            self.y = new_y
            move -= direction

            # Non-solid collisions
            self._invoke_non_solid_collisions(self.x, self.y)

    def move(self, x: int, y: int) -> None:
        """ Move the entity to a position, and invoke collisions at the new position.
        This teleports the entity without checking for collision along the way.
        """
        self.x = x
        self.y = y
        self._invoke_solid_collisions(self.x, self.y)
        self._invoke_non_solid_collisions(self.x, self.y)

    # Internal methods

    def _collisions_pre_update(self) -> None:
        """ Reset the collision tracking for this frame. """
        self._collisions_last_frame = self._collisions_this_frame.copy()
        self._collisions_this_frame.clear()

    def _mouse_pre_update(self) -> None:
        """ Reset the mouse tracking for this frame. """
        self._mouse_last_frame = self._mouse_this_frame
        self._mouse_this_frame = False

    def _collisions_post_update(self) -> None:
        """ Handle persistent collisions.

        If an entity was collided with last frame and this frame, we call 'on_collision_stay'.
        Because we normally only update collisions during movement, we first need to double-check the collision against
        anything that was in the collision list in the last frame, so that we don't miss anything.

        Once we've ruled out the persistent collisions, then we can safely call 'on_collision_end'.
        """
        for entity in self._collisions_last_frame - self._collisions_this_frame:
            if self._check_collision_at(self.x, self.y, entity):
                self._collisions_this_frame.add(entity)

        for entity in self._collisions_last_frame:
            if entity in self._collisions_this_frame:
                self.on_collision_stay(entity)
            else:
                self.on_collision_end(entity)

    def _mouse_post_update(self) -> None:
        """ Check for mouse collision, for each camera that can draw this entity. """
        # Check collisions with each active camera
        if self.active:
            if self.mouse_collisions_enabled and Mouse.in_viewport():
                for camera in self.scene.cameras.active_cameras():
                    if camera.can_draw_entity(self):
                        if self.bbox().contains_point(Mouse.world_position(camera)):
                            self._mouse_this_frame = True

        # Invoke callbacks
        if self._mouse_this_frame and not self._mouse_last_frame:
            self.on_mouse_enter()
        elif self._mouse_this_frame:
            self.on_mouse_over()
        elif not self._mouse_this_frame and self._mouse_last_frame:
            self.on_mouse_exit()

    def _invoke_solid_collisions(self, x: int, y: int) -> bool:
        """ Invoke all possible collisions at a given position.
        This returns True if at least one collision is invoked.
        """
        collision_invoked = False
        for entity in self._get_solid_collisions(x, y):
            self._register_collision(entity)
            entity._register_collision(self)
            collision_invoked = True

        return collision_invoked

    def _invoke_non_solid_collisions(self, x: int, y: int) -> bool:
        """ Invoke all possible non-solid collisions at a given position.
        This returns True if at least one collision is invoked.
        """
        collision_invoked = False
        for entity in self._get_non_solid_collisions(x, y):
            self._register_collision(entity)
            entity._register_collision(self)
            collision_invoked = True

        return collision_invoked

    def _get_solid_collisions(self, x: int, y: int) -> Iterator[Entity]:
        """ Get a list of solid entities that the actor would collide with at a given position. """
        for entity in self.scene.entities.active_entities():
            if entity == self:
                continue
            if not entity.solid:
                continue
            if self._check_collision_at(x, y, entity):
                yield entity

    def _get_non_solid_collisions(self, x: int, y: int) -> Iterator[Entity]:
        """ Get a list of non-solid entities that the actor would collide with at a given position. """
        for entity in self.scene.entities.active_entities():
            if entity == self:
                continue
            if entity.solid:
                continue
            if self._check_collision_at(x, y, entity):
                yield entity

    def _check_collision_at(self, x: int, y: int, other: Entity) -> bool:
        """ Check if this entity, at a given position, will intersect another entity. """
        if not self.active or not other.active:
            return False

        if not self.collisions_enabled or not other.collisions_enabled:
            return False

        bbox = Rect(x, y, self.width, self.height)
        return other.intersects(bbox)

    def _register_collision(self, other: Entity) -> None:
        """ Registers a collision between this entity and another entity. """
        # If we have already handled a collision against a specific entity this frame, prevent it from being run again
        if other in self._collisions_this_frame:
            return

        self._collisions_this_frame.add(other)

        # Check to see if this is the first frame of collision
        if other not in self._collisions_last_frame:
            self.on_collision_begin(other)
