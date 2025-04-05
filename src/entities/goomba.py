from potion import *

from entities.enemy import Enemy
from entities.score_fx import ScoreFx


class Goomba(Enemy):
    def __init__(self) -> None:
        super().__init__()

        self.sprite = AnimatedSprite.from_atlas("atlas.png", "goomba")
        self.sprite.play("Walk")

        self.collisions_enabled = True
        self.width = 10
        self.height = 9

        self.dx = -.2

    def update(self) -> None:
        self.sprite.update()

        if self.dx <= 0:
            self.sprite.flip_horizontal = True
        else:
            self.sprite.flip_horizontal = False

        self.move_x(self.dx)

    def draw(self, camera: Camera) -> None:
        self.sprite.draw(camera, self.position() - Point(1, 1))

    def on_death(self) -> None:
        fx = ScoreFx.instantiate()
        fx.set_position(self.position())
