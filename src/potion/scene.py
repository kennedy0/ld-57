from __future__ import annotations
from typing import Iterator

from ulid import ULID

from potion.camera import Camera
from potion.camera_list import CameraList
from potion.entity_list import EntityList
from potion.level import Level
from potion.log import Log


class Scene:
    """ A scene is a group of entities that the engine is processing. """
    def __init__(self) -> None:
        self._name = f"{self.__class__.__name__}-{ULID()}"
        self._frame = 0
        self._paused = False
        self._cameras = CameraList(self)
        self._entities = EntityList(self)
        self._level_map = {}

        self._main_camera = None
        self._ui_camera = None

        self._init_default_cameras()

    def __str__(self) -> str:
        return f"Scene({self.name})"

    def __repr__(self) -> str:
        return str(self)

    @property
    def name(self) -> str:
        """ The name of the scene. """
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def frame(self) -> int:
        """ The current frame number of the scene. """
        return self._frame

    @property
    def paused(self) -> bool:
        """ If True, the scene is paused. """
        return self._paused

    @paused.setter
    def paused(self, value: bool) -> None:
        self._paused = value

    @property
    def main_camera(self) -> Camera:
        """ The main camera for the scene. """
        return self._main_camera

    @property
    def ui_camera(self) -> Camera:
        """ The UI camera for the scene. """
        return self._ui_camera

    @property
    def cameras(self) -> CameraList:
        """ A list of cameras in the scene. """
        return self._cameras

    @property
    def entities(self) -> EntityList:
        """ A list of entities in the scene. """
        return self._entities

    @property
    def levels(self) -> Iterator[Level]:
        """ Iterate over the levels. """
        for level in self._level_map.values():
            yield level

    def _init_default_cameras(self) -> None:
        """ Initialize the default cameras.
        This creates the "Main" and "UI" cameras.
        """
        self._main_camera = Camera("Main", 0)
        self._main_camera.exclude_tag("UI")
        self.cameras.add(self._main_camera)

        self._ui_camera = Camera("UI", -1000)
        self._ui_camera.include_tag("UI")
        self.cameras.add(self._ui_camera)

    def get_level(self, level_name: str) -> Level | None:
        """ Get a level by name. """
        return self._level_map.get(level_name)

    def setup_cameras(self) -> None:
        """ Use this to add cameras to the scene and/or change camera settings.
        This is called right before `load_entities`.
        """
        pass

    def load_entities(self) -> None:
        """ Use this to load entities into the scene.
        This is called right before `start`.
        """
        pass

    def add_level(self, level: Level) -> None:
        """ Add a level to the scene. """
        level._scene = self
        self._level_map[level.name] = level

    def remove_level(self, level: Level) -> None:
        """ Remove a level from the scene. """
        try:
            for entity in list(level.entities):
                level.remove_entity(entity)
            level._scene = None
            del self._level_map[level.name]
        except KeyError:
            Log.error(f"{level} is not in {self}")

    def on_load(self) -> None:
        """ Called when the engine loads the scene. """
        self.setup_cameras()
        self.cameras.flag_list_needs_sorting()
        self.cameras.update_list()

        self.load_entities()
        self.entities.flag_entity_draw_list_needs_sorting()
        self.entities.update_list()

    def start(self) -> None:
        """ Called right after the engine loads the scene. """
        pass

    def update(self) -> None:
        """ Update loop. """
        self.cameras.update_list()
        self.entities.update_list()
        self.entities.update()

    def draw(self) -> None:
        """ Draw loop. """
        for camera in self.cameras.active_cameras():
            camera.draw(self.entities)

    def end(self) -> None:
        """ Called before the engine loads the next scene. """
        pass
