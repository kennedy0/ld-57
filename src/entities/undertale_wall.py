from potion import *


class UndertaleWall(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.tags.add("UndertaleWall")
        self.solid = True
        self.collisions_enabled = True

    def debug_draw(self, camera: Camera) -> None:
        self.bbox().draw(camera, Color.red())
