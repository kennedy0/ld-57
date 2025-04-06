from potion import *

from entities.score_fx import ScoreFx


class Rupee(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.tags.add("Rupee")

        self.amount = 1
        self.sprite = Sprite.from_atlas("atlas.png", "rupee")

        self.collisions_enabled = False
        self.width = 6
        self.height = 10

        self.timer = 5
        self.z = -2

    def awake(self) -> None:
        if self.amount == 20:
            self.sprite = Sprite.from_atlas("atlas.png", "rupee20")
        elif self.amount == 5:
            self.sprite = Sprite.from_atlas("atlas.png", "rupee5")

    def update(self) -> None:
        self.timer -= 1
        if self.timer <= 0:
            self.collisions_enabled = True

    def draw(self, camera: Camera) -> None:
        self.sprite.draw(camera, self.position())

    def on_collect(self) -> None:
        try:
            if player := self.find("Player"):
                player.rupees += self.amount
        except:
            pass

        self.destroy()

