import random

from potion import *

from entities.grass_fx import GrassFx


class Grass(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.collisions_enabled = True
        self.width = 8
        self.height = 8

        self.sprite = Sprite.from_atlas("atlas.png", random.choice(["grass_a", "grass_b", "grass_c"]))
        self.cut_sprite = Sprite.from_atlas("atlas.png", "grass_cut")
        if pmath.random_bool():
            self.sprite.flip_horizontal = True

        self.is_cut = False

        self.timer = 0
        self.max_timer_a = 600
        self.max_timer_b = 1200

    def cut(self) -> None:
        if self.is_cut:
            return

        self.is_cut = True

        points = (
            self.position() + Point(0, 0),
            self.position() + Point(4, 0),
            self.position() + Point(0, 4),
            self.position() + Point(4, 4),
        )

        velocities = (
            Vector2(-0.5, -0.5),
            Vector2(0.5, -0.5),
            Vector2(-0.5, -.25),
            Vector2(-0.5, -.25),
        )

        for p, v in zip(points, velocities):
            fx = GrassFx.instantiate()
            fx.set_position(p)
            fx.velocity = v

        self.timer = random.randint(self.max_timer_a, self.max_timer_b)

    def update(self) -> None:
        self.timer -= 1
        if self.timer <= 0:
            self.is_cut = False

    def draw(self, camera: Camera) -> None:
        if self.is_cut:
            self.cut_sprite.draw(camera, self.position())
        else:
            self.sprite.draw(camera, self.position())
