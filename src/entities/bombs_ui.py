from __future__ import annotations

from potion import *

if TYPE_CHECKING:
    from entities.player import Player


class BombsUi(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.tags.add("UI")

        self.player: Player | None = None

        self.sprite = Sprite.from_atlas("atlas.png", "bomb")
        self.text = Text("fonts/m5x7.16.png")
        self.text.text = "x 0"
        self.has_bomb = False

        self.sprite_position = Point(9, 42)
        self.text_position = Point(20, 40)

    def start(self) -> None:
        self.player = self.find("Player")

    def update(self) -> None:
        try:
            if self.player.has_bomb != self.has_bomb:
                self.has_bomb = self.player.has_bomb
                if self.has_bomb:
                    self.text.text = "x 1"
                else:
                    self.text.text = "x 0"
        except:
            pass

    def draw(self, camera: Camera) -> None:
        self.sprite.draw(camera, self.sprite_position)
        self.text.draw(camera, self.text_position)
