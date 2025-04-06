from potion import *

from entities.mario_brick_fx import MarioBrickFx


class CrackedBlock(Entity):
    def __init__(self) -> None:
        super().__init__()

        self.collisions_enabled = True
        self.solid = True
        self.width = 8
        self.height = 8

        self.sprite = Sprite.from_atlas("atlas.png", "cracked_block")

    def draw(self, camera: Camera) -> None:
        self.sprite.draw(camera, self.position())

    def damage(self):
        self.destroy()

        points = (
            self.position() + Point(0, 0),
            self.position() + Point(4, 0),
            self.position() + Point(0, 4),
            self.position() + Point(4, 4),
        )

        velocities = (
            Vector2(-1, -1),
            Vector2(1, -1),
            Vector2(-1, -.5),
            Vector2(-1, -.5),
        )

        for p, v in zip(points, velocities):
            brick = MarioBrickFx.instantiate()
            brick.set_position(p)
            brick.velocity = v
