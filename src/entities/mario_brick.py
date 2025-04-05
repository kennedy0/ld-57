from potion import *

from entities.mario_brick_fx import MarioBrickFx


class MarioBrick(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.sprite = Sprite.from_atlas("atlas.png", "mario_brick")

        self.collisions_enabled = True
        self.solid = True
        self.width = 8
        self.height = 8

    def on_head_hit(self) -> None:
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

    def draw(self, camera: Camera) -> None:
        self.sprite.draw(camera, self.position())
