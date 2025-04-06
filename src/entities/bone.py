from potion import *


class Bone(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.tags.add("Enemy")

        self.delay = 0

        self.sprite = AnimatedSprite.from_atlas("atlas.png", "bone")
        self.sprite.play("default")

        self.timer = self.delay
        self.waiting = True

        self.collisions_enabled = True
        self.solid = False
        self.width = 16
        self.height = 16

        self.speed = 1

    def awake(self) -> None:
        self.timer = self.delay

    def update(self) -> None:
        self.sprite.update()

        self.timer -= 1
        if self.timer <= 0:
            self.waiting = False

        if self.waiting:
            return

        self.move(self.x, self.y + self.speed)

    def draw(self, camera: Camera) -> None:
        self.sprite.draw(camera, self.position())

    def debug_draw(self, camera: Camera) -> None:
        self.bbox().draw(camera, Color.red())
