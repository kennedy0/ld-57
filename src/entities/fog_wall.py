from potion import *


class FogWall(Entity):
    def __init__(self) -> None:
        super().__init__()

        self.sprite = AnimatedSprite.from_atlas("atlas.png", "fog_wall")
        self.sprite.play("default")

        self.collisions_enabled = False
        self.solid = False
        self.width = 8
        self.height = 64

        self.player: Entity | None = None

    def start(self) -> None:
        self.player = self.find("Player")

    def update(self) -> None:
        self.sprite.update()

        if not self.collisions_enabled:
            if self.player.x >= self.bbox().right():
                self.collisions_enabled = True
                self.solid = True

    def draw(self, camera: Camera) -> None:
        self.sprite.draw(camera, self.position())
