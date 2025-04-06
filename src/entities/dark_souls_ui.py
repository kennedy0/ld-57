from __future__ import annotations

from potion import *

if TYPE_CHECKING:
    from entities.player import Player


class DarkSoulsUi(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.tags.add("UI")

        self.player: Player | None = None

        self.sprite_3 = Sprite.from_atlas("atlas.png", "dark_souls_hp_3")
        self.sprite_2 = Sprite.from_atlas("atlas.png", "dark_souls_hp_2")
        self.sprite_1 = Sprite.from_atlas("atlas.png", "dark_souls_hp_1")
        self.sprite_0 = Sprite.from_atlas("atlas.png", "dark_souls_hp_0")

        self.sprite_position = Point(4, 4)

    def start(self) -> None:
        self.player = self.find("Player")

    def draw(self, camera: Camera) -> None:
        if self.player.hp == 3:
            self.sprite_3.draw(camera, self.sprite_position)
        if self.player.hp == 2:
            self.sprite_2.draw(camera, self.sprite_position)
        if self.player.hp == 1:
            self.sprite_1.draw(camera, self.sprite_position)
        if self.player.hp == 0:
            self.sprite_0.draw(camera, self.sprite_position)
