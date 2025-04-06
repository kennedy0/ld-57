import random

from potion import *

from entities.grass_fx import GrassFx
from entities.rupee import Rupee


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

        self.z = -2

    def cut(self) -> None:
        if self.is_cut:
            return

        self.is_cut = True
        self.collisions_enabled = False

        for _ in range(4):
            fx = GrassFx.instantiate()
            fx.set_position(self.bbox().center())
            vx = (random.random() - .5)
            vy = (random.random() - .5)
            fx.velocity = Vector2(vx, vy)

        self.timer = random.randint(self.max_timer_a, self.max_timer_b)

        rng = random.randint(0, 100)
        amount = 0
        if rng > 95:
            amount = 20
        elif rng > 80:
            amount = 5
        elif rng > 50:
            amount = 1

        if amount:
            rupee = Rupee.instantiate()
            rupee.amount = amount
            rx = self.x + 1
            ry = self.y - 2
            rupee.set_position(Point(rx, ry))

    def update(self) -> None:
        self.timer -= 1
        if self.timer <= 0:
            self.is_cut = False
            self.collisions_enabled = True

    def draw(self, camera: Camera) -> None:
        p = Point(1, 2)
        if self.is_cut:
            self.cut_sprite.draw(camera, self.position() + p)
        else:
            self.sprite.draw(camera, self.position() + p)

    def on_collision_begin(self, other: Entity) -> None:
        if "Sword" in other.tags:
            self.cut()
