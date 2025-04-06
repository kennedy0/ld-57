import random

from potion import *


class GrassFx(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.sprite = Sprite.from_atlas("atlas.png", "grass_fx")
        if pmath.random_bool():
            self.sprite.flip_horizontal = True
        if pmath.random_bool():
            self.sprite.flip_vertical = True

        self.timer = 30

        self.gravity = .01
        self.velocity = Vector2.zero()
        self.dx = 0
        self.dy = 0

    def awake(self) -> None:
        self.timer = random.randint(20, 100)
        self.dx = self.velocity.x
        self.dy = self.velocity.y

    def update(self) -> None:
        self.timer -= 1

        if self.timer <= 0:
            self.destroy()

        self.dy += self.gravity
        self.move_y(self.dy)
        self.move_x(self.dx)

    def draw(self, camera: Camera) -> None:
        self.sprite.draw(camera, self.position())
