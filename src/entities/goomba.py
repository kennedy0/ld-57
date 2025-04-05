from potion import *

from entities.enemy import Enemy
from entities.goomba_fx import GoombaFx


class Goomba(Enemy):
    def __init__(self) -> None:
        super().__init__()

        self.sprite = AnimatedSprite.from_atlas("atlas.png", "goomba")
        self.sprite.play("Walk")

        self.collisions_enabled = True
        self.width = 10
        self.height = 9

    def update(self) -> None:
        self.sprite.update()

    def draw(self, camera: Camera) -> None:
        self.sprite.draw(camera, self.position() - Point(1, 1))

    def on_death(self) -> None:
        fx = GoombaFx.instantiate()
        fx.set_position(self.position())
