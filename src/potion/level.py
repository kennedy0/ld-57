from __future__ import annotations

from typing import Iterator, TYPE_CHECKING

from potion.data_types.rect import Rect
from potion.entity import Entity
from potion.log import Log

if TYPE_CHECKING:
    from potion.scene import Scene


class Level:
    """ A level is a subsection of a scene.

    It contains a mapping of entities that belong to it, which can help manage scene complexity, reduce update and draw
    calls, manage camera transitions, etc.
    """
    def __init__(self, name: str, x: int, y: int, width: int, height: int) -> None:
        self._scene = None
        self._name = name
        self._x = int(x)
        self._y = int(y)
        self._width = int(width)
        self._height = int(height)

        self._depth = 0
        self._entities = {}

        # Neighbors track the levels that are neighboring this one
        # 'above' and 'below' are for worlds that have layered levels with multiple Z-depth values
        self._neighbors = {
            'north': [],
            'south': [],
            'east': [],
            'west': [],
            'northeast': [],
            'northwest': [],
            'southeast': [],
            'southwest': [],
            'above': [],
            'below': [],
        }  # type: dict[str, list[Level]]

        # Arbitrary metadata
        self.metadata = {}

    def __str__(self) -> str:
        return f"Level({self.name})"

    def __repr__(self) -> str:
        return str(self)

    @property
    def scene(self) -> Scene | None:
        """ The scene that the level belongs to. """
        return self._scene

    @property
    def name(self) -> str:
        """ The name of the level. """
        return self._name

    @property
    def x(self) -> int:
        """ The X position of the level. """
        return self._x

    @property
    def y(self) -> int:
        """ The Y position of the level. """
        return self._y

    @property
    def width(self) -> int:
        """ The width of the level. """
        return self._width

    @property
    def height(self) -> int:
        """ The height of the level. """
        return self._height

    @property
    def depth(self) -> int:
        """ The Z-depth of the level.
        Lower (negative) numbers represent layers that are on top of higher (positive) numbers:
            Top ->     -2
                       -1
            Default ->  0
                        1
            Bottom ->   2
        """
        return self._depth

    @depth.setter
    def depth(self, value: int) -> None:
        self._depth = int(value)

    @property
    def north(self) -> list[Level]:
        """ Neighboring levels north of this one. """
        return self._neighbors['north']

    @property
    def south(self) -> list[Level]:
        """ Neighboring levels south of this one. """
        return self._neighbors['south']

    @property
    def east(self) -> list[Level]:
        """ Neighboring levels east of this one. """
        return self._neighbors['east']

    @property
    def west(self) -> list[Level]:
        """ Neighboring levels west of this one. """
        return self._neighbors['west']

    @property
    def northeast(self) -> list[Level]:
        """ Neighboring levels northeast of this one. """
        return self._neighbors['northeast']

    @property
    def northwest(self) -> list[Level]:
        """ Neighboring levels northwest of this one. """
        return self._neighbors['northwest']

    @property
    def southeast(self) -> list[Level]:
        """ Neighboring levels southeast of this one. """
        return self._neighbors['southeast']

    @property
    def southwest(self) -> list[Level]:
        """ Neighboring levels southwest of this one. """
        return self._neighbors['southwest']

    @property
    def above(self) -> list[Level]:
        """ Neighboring levels above this one. """
        return self._neighbors['above']

    @property
    def below(self) -> list[Level]:
        """ Neighboring levels below this one. """
        return self._neighbors['below']

    @property
    def all_neighbors(self) -> list[Level]:
        """ All neighboring levels """
        all_neighbors = []
        for neighbors in self._neighbors.values():
            all_neighbors += neighbors

        return all_neighbors

    @property
    def entities(self) -> Iterator[Entity]:
        """ Iterate over the entities in the level. """
        for entity in self._entities.values():
            yield entity

    def rect(self) -> Rect:
        """ The rectangular region that this level occupies. """
        return Rect(self._x, self._y, self._width, self._height)

    def add_entity(self, entity: Entity) -> None:
        """ Add an entity to the level. """
        if entity.level:
            Log.error(f"{entity} already belongs to {entity.level}")
            return

        entity._level = self
        self._entities.update({entity.name: entity})

    def remove_entity(self, entity: Entity) -> None:
        """ Remove an entity from the level. """
        try:
            entity = self._entities.pop(entity.name)
            entity._level = None
        except KeyError:
            Log.error(f"{entity} is not in {self}")

    def add_neighbor(self, level: Level, location: str) -> None:
        """ Add a neighboring level.
        This is NOT bidirectional - it needs to be called on both levels for them to be properly linked.
        """
        # Make sure a valid location is given
        valid_locations = list(self._neighbors.keys())
        if location not in valid_locations:
            Log.error(f"'{location}' is not a valid location; must be one of: {valid_locations}")
            return

        # Make sure the neighbor isn't already linked
        for direction, neighbors in self._neighbors.items():
            if level in neighbors:
                Log.error(f"'{level}' is already a '{direction}' neighbor of {self}")
                return

        # Add the level as a neighbor
        self._neighbors[location].append(level)

    def remove_neighbor(self, level: Level) -> None:
        """ Remove a neighboring level.
        This is NOT bidirectional - it needs to be called on both levels for them to be properly unlinked.
        """
        for direction, neighbors in self._neighbors.items():
            if level in neighbors:
                neighbors.remove(level)

    def get_entity(self, entity_name: str) -> Entity | None:
        """ Get an entity from the level by name. """
        return self._entities.get(entity_name)

    def set_entities_active(self, value: bool) -> None:
        """ Set the active status on all entities in the level. """
        for entity in self.entities:
            entity.active = value

    def move(self, x: int, y: int, move_entities: bool = True) -> None:
        """ Move the level.
        If `move_entities` is True, all entities in the level will be moved as well.
        """
        dx = x - self.x
        dy = y - self.y

        self._x = x
        self._y = y

        if move_entities:
            for entity in self.entities:
                entity.x += dx
                entity.y += dy

    def destroy(self, destroy_entities: bool = True) -> None:
        """ Remove this level from the scene.
        If `destroy_entities` is True, all entities in the level will be destroyed as well.
        """
        if destroy_entities:
            for entity in self.entities:
                entity.destroy()

        self.scene.remove_level(self)
