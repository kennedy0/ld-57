from potion.camera import Camera
from potion.entity import Entity
from potion.sprite import Sprite


class LDtkSimplifiedTilesEntity(Entity):
    """ An LDtk Tiles layer from a 'Super Simple Export'. """
    def __init__(self) -> None:
        super().__init__()
        self.tags.add("ldtk")
        self.tags.add("ldtk_tiles")
        self.sprite = Sprite.empty()

    def draw(self, camera: Camera) -> None:
        self.sprite.draw(camera, self.position())
