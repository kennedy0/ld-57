from __future__ import annotations

from typing import Iterator, TYPE_CHECKING

if TYPE_CHECKING:
    from potion.camera import Camera
    from potion.scene import Scene


class CameraList:
    """ A specialized list for managing cameras in the main game loop. """
    def __init__(self, scene: Scene) -> None:
        self._scene = scene

        # List of cameras
        self._camera_list: list[Camera] = []
        self._camera_map: dict[str, Camera] = {}

        self._needs_sorting = False

        # Lists for add / remove queue
        self._to_add: list[Camera] = []
        self._to_remove: list[Camera] = []

        # Sets to quickly check list membership
        self._current: set[Camera] = set()
        self._adding: set[Camera] = set()
        self._removing: set[Camera] = set()

    def __str__(self) -> str:
        return f"CameraList({len(self)} items)"

    def __repr__(self) -> str:
        return str(self)

    def __len__(self) -> int:
        return len(self._camera_list)

    def __iter__(self) -> Iterator[Camera]:
        for camera in self._camera_list:
            yield camera

    def active_cameras(self) -> Iterator[Camera]:
        """ Iterate over active cameras. """
        for camera in self:
            if camera.active:
                yield camera

    def add(self, camera: Camera) -> None:
        """ Add a camera to the list. """
        self._validate_name(camera)
        self._validate_draw_order(camera)

        if camera not in self._current and camera not in self._adding:
            self._to_add.append(camera)
            self._adding.add(camera)
            self.flag_list_needs_sorting()

    def _validate_name(self, camera: Camera) -> None:
        """ Make sure the camera has a unique name. """
        for existing_camera in self._camera_list + self._to_add:
            if camera.name == existing_camera.name:
                raise RuntimeError(f"Camera with name {camera.name} has already been added to the scene.")

    def _validate_draw_order(self, camera: Camera) -> None:
        """ Make sure the camera has a unique draw order. """
        for existing_camera in self._camera_list + self._to_add:
            if camera.draw_order == existing_camera.draw_order:
                raise RuntimeError(f"{camera} has the same draw order as {existing_camera}")

    def remove(self, camera: Camera) -> None:
        """ Remove a camera from the list. """
        if camera in self._current and camera not in self._removing:
            self._to_remove.append(camera)
            self._removing.add(camera)

    def flag_list_needs_sorting(self) -> None:
        """ Flag that the camera list needs to be sorted. """
        self._needs_sorting = True

    def get(self, camera_name: str) -> Camera | None:
        """ Get a camera by name. """
        return self._camera_map.get(camera_name)

    def update_list(self) -> None:
        """ This handles the logic for adding and removing cameras from the list.
        The process is deferred until the start of the next frame.
        """
        # Add queued cameras
        for camera in self._to_add:
            self._camera_list.append(camera)
            self._camera_map[camera.name] = camera
            self._current.add(camera)
            camera._scene = self._scene

        # Remove queued cameras
        for camera in self._to_remove:
            self._camera_list.remove(camera)
            self._camera_map.pop(camera.name)
            self._current.remove(camera)
            camera._scene = None

        # Camera lifecycle methods
        for camera in self._to_add:
            camera.start()

        # Sort
        if self._needs_sorting:
            self.sort()

        # Clear lists
        self._to_add.clear()
        self._adding.clear()
        self._to_remove.clear()
        self._removing.clear()

    def sort(self) -> None:
        """ Sort the camera list based on the draw order. """
        self._camera_list.sort(key=lambda c: c.draw_order, reverse=True)
        self._needs_sorting = False
