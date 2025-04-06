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

        self.timer = 0

    def update(self) -> None:
        self.sprite.update()

        self.timer -= 1
        if self.timer <= 0:
            self.timer = 0

    def draw(self, camera: Camera) -> None:
        if self.timer:
            if self.timer > 10:
                self.sprite.draw(camera, self.position() + Point(0, -1))
            elif self.timer > 5:
                self.sprite.draw(camera, self.position() + Point(0, -2))
            else:
                self.sprite.draw(camera, self.position() + Point(0, -1))
        else:
            self.sprite.draw(camera, self.position())

    def on_collect(self) -> None:
        try:
            if player := self.find("Player"):
                player.coins += 1
        except:
            pass

        fx = ScoreFx.instantiate()
        fx.set_position(self.position())
        self.destroy()
