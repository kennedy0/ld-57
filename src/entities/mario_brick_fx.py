import random

from potion import *


class MarioBrickFx(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.sprite = Sprite.from_atlas("atlas.png", "mario_brick_fx")
        self.timer = 60

        self.gravity = .1
        self.velocity = Vector2.zero()
        self.dx = 0
        self.dy = 0

    def awake(self) -> None:
        self.timer = random.randint(20, 100)

        rx = ((random.random() * 2) - 1)
        ry = ((random.random() * 2) - 1)

        self.dx = self.velocity.x + rx
        self.dy = (self.velocity.y * 3) + ry

    def update(self) -> None:
        self.timer -= 1

        if self.timer <= 0:
            self.destroy()

        self.dy += self.gravity
        self.move_y(self.dy)
        self.move_x(self.dx)

    def draw(self, camera: Camera) -> None:
        self.sprite.draw(camera, self.position())
