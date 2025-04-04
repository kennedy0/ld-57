from __future__ import annotations

from typing import Iterator, TYPE_CHECKING

from potion.entity import Entity
from potion.log import Log

if TYPE_CHECKING:
    from potion.camera import Camera
    from potion.scene import Scene


class EntityList:
    """ A specialized list for managing entities in the main game loop. """
    def __init__(self, scene: Scene) -> None:
        self._scene = scene

        # When we are mid-update, handle EntityList changes in separate lists.
        # This is needed to prevent the update logic from skipping some entities. For example: An entity adding another
        #   entity to the scene during its `awake` method.
        self._is_updating = False
        self._added_while_updating: list[Entity] = []
        self._removed_while_updating: list[Entity] = []

        # List of entities
        self._entity_list: list[Entity] = []
        self._entity_map: dict[str, Entity] = {}

        # A Z-sorted list of entities for the draw loop
        self._entity_draw_list: list[Entity] = []
        self._entity_draw_list_needs_sorting = False

        # Add / remove queue
        self._to_add: list[Entity] = []
        self._to_remove: list[Entity] = []
        self._name_to_add: set[str] = set()

        # Active / inactive queue
        self._to_activate: list[Entity] = []
        self._to_deactivate: list[Entity] = []

    def __str__(self) -> str:
        return f"EntityList({len(self)} items)"

    def __repr__(self) -> str:
        return str(self)

    def __len__(self) -> int:
        return len(self._entity_list)

    def __iter__(self) -> Iterator[Entity]:
        for entity in self._entity_list:
            yield entity

    def active_entities(self) -> Iterator[Entity]:
        """ Iterate over active entities. """
        for entity in self:
            if entity.active:
                yield entity

    def add(self, entity: Entity) -> None:
        """ Add an entity to the list. """
        if self._is_updating:
            self._added_while_updating.append(entity)
            return

        if entity.name in self._name_to_add:
            Log.error(f"Cannot add {entity}; an entity named '{entity.name}' already exists")
            return

        if entity not in self._entity_list and entity not in self._to_add:
            self._to_add.append(entity)
            self._name_to_add.add(entity.name)
            self.flag_entity_draw_list_needs_sorting()

    def remove(self, entity: Entity) -> None:
        """ Remove an entity from the list. """
        if self._is_updating:
            self._removed_while_updating.append(entity)
            return

        if entity in self._entity_list and entity not in self._to_remove:
            self._to_remove.append(entity)

    def set_active(self, entity: Entity) -> None:
        """ Activate an entity in the list. """
        if entity in self._to_deactivate:
            self._to_deactivate.remove(entity)

        if entity not in self._to_activate:
            self._to_activate.append(entity)

    def set_inactive(self, entity: Entity) -> None:
        """ Deactivate an entity in the list. """
        if entity in self._to_activate:
            self._to_activate.remove(entity)

        if entity not in self._to_deactivate:
            self._to_deactivate.append(entity)

    def rename(self, old_name: str, new_name: str) -> bool:
        """ Rename an entity.
        Returns True if successful, otherwise returns False.
        """
        if old_name not in self._entity_map:
            Log.error(f"Cannot rename '{old_name}' to '{new_name}'; '{old_name}' does not exist in the entity list")
            return False

        if new_name in self._entity_map:
            Log.error(f"Cannot rename '{old_name}' to '{new_name}'; an entity named '{new_name}' already exists")
            return False

        self._entity_map[new_name] = self._entity_map.pop(old_name)
        return True

    def flag_entity_draw_list_needs_sorting(self) -> None:
        """ Flag that the entity draw list needs to be sorted. """
        self._entity_draw_list_needs_sorting = True

    def get(self, entity_name: str) -> Entity | None:
        """ Get an entity by name. """
        return self._entity_map.get(entity_name)

    def update_list(self) -> None:
        """ This handles the logic for adding and removing entities from the list.
        The process is deferred until the start of the next frame.
        """
        self._is_updating = True

        # Add queued entities
        for entity in self._to_add:
            self._entity_list.append(entity)
            self._entity_draw_list.append(entity)
            self._entity_map[entity.name] = entity
            self.set_active(entity)
            entity._scene = self._scene

        # Remove queued entities
        for entity in self._to_remove:
            self._entity_list.remove(entity)
            self._entity_draw_list.append(entity)
            self._entity_map.pop(entity.name)
            self.set_inactive(entity)
            entity._scene = None

        # Entity lifecycle methods
        for entity in self._to_add:
            entity.awake()

        for entity in self._to_activate:
            entity._active = True
            entity.on_activate()

        for entity in self._to_add:
            entity.start()
            entity._started = True

        for entity in self._to_deactivate:
            entity._active = False
            entity.on_deactivate()

        for entity in self._to_remove:
            entity.end()

        # Sort
        if self._entity_draw_list_needs_sorting:
            self.sort_draw_list()

        # Clear lists
        self._to_add.clear()
        self._to_remove.clear()
        self._name_to_add.clear()
        self._to_activate.clear()
        self._to_deactivate.clear()

        self._is_updating = False

        # Add any entities to the add/remove queues that were done during this update, so they can be handled next frame
        if self._added_while_updating or self._removed_while_updating:
            for entity in self._added_while_updating:
                self.add(entity)

            for entity in self._removed_while_updating:
                self.remove(entity)

            self._added_while_updating.clear()
            self._removed_while_updating.clear()

    def sort_draw_list(self) -> None:
        """ Sort the entity draw list based on their Z position. """
        self._entity_draw_list.sort(key=lambda e: e.z, reverse=True)
        self._entity_draw_list_needs_sorting = False

    def update(self) -> None:
        """ Update loop. """
        # Reset collision information
        for entity in self:
            if self._scene.paused and entity.pausable:
                continue
            entity._collisions_pre_update()  # noqa
            entity._mouse_pre_update()  # noqa

        # Update
        for entity in self.active_entities():
            if self._scene.paused and entity.pausable:
                continue
            entity.update()

        # Handle collision callbacks
        for entity in self:
            if self._scene.paused and entity.pausable:
                continue
            entity._collisions_post_update()  # noqa
            entity._mouse_post_update()  # noqa

    def draw(self, camera: Camera) -> None:
        """ Draw loop. """
        for entity in self._entity_draw_list:
            if entity.active:
                if camera.can_draw_entity(entity):
                    entity.draw(camera)

    def debug_draw(self, camera: Camera) -> None:
        """ Debug draw pass. """
        for entity in self._entity_draw_list:
            if entity.active:
                if camera.can_draw_entity(entity):
                    entity.debug_draw(camera)

    def end(self) -> None:
        """ Called when the scene ends. """
        for entity in self:
            if entity.active:
                entity.on_deactivate()

        for entity in self:
            entity.end()
