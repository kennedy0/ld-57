from potion import *

from entities.key_fx import KeyFx


class Chest(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.tags.add("Chest")

        self.sprite_closed = Sprite.from_atlas("atlas.png", "chest_closed")
        self.sprite_open = Sprite.from_atlas("atlas.png", "chest_open")

        self.open = False

        self.collisions_enabled = True
        self.width = 16
        self.height = 16

        self.sfx = SoundEffect("music/zeldachest.wav")

    def draw(self, camera: Camera) -> None:
        if self.open:
            self.sprite_open.draw(camera, self.position())
        else:
            self.sprite_closed.draw(camera, self.position())

    def on_collect(self) -> None:
        if self.open:
            return

        try:
            if player := self.find("Player"):
                player.keys += 1
                fx = KeyFx.instantiate()
                fx.set_position(player.bbox().center() + Point(0, -14))
                self.sfx.play()
        except:
            pass

        self.collisions_enabled = False
        self.open = True
