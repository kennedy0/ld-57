from potion import *

from entities.undertale_wall import UndertaleWall


class UndertaleBox(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.name = "UndertaleBox"
        self.sprite = Sprite.from_atlas("atlas.png", "undertale_box")

    def awake(self) -> None:
        bottom = UndertaleWall.instantiate()
        bottom.width = self.width
        bottom.height = 8
        bottom.x = self.x
        bottom.y = self.y + self.height - 1

    def create_walls(self) -> None:
        left = UndertaleWall.instantiate()
        left.width = 8
        left.height = self.height
        left.x = self.x - left.width + 2
        left.y = self.y

        right = UndertaleWall.instantiate()
        right.width = 8
        right.height = self.height
        right.x = self.x + self.width - 2
        right.y = self.y

    def destroy_walls(self) -> None:
        for entity in self.scene.entities:
            if "UndertaleWall" in entity.tags:
                entity.destroy()

    def draw(self, camera: Camera) -> None:
        self.sprite.draw(camera, self.position())
