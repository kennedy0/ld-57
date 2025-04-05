from potion import *

from entities.score_fx import ScoreFx


class MarioCoin(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.tags.add("Coin")
        self.sprite = AnimatedSprite.from_atlas("atlas.png", "coin")
        self.sprite.play("default")

        self.collisions_enabled = True
        self.width = 8
        self.height = 8

    def update(self) -> None:
        self.sprite.update()

    def draw(self, camera: Camera) -> None:
        self.sprite.draw(camera, self.position())

    def on_deactivate(self) -> None:
        fx = ScoreFx.instantiate()
        fx.set_position(self.position())
