from __future__ import annotations

from potion import *

if TYPE_CHECKING:
    from entities.player import Player


class KeysUi(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.tags.add("UI")

        self.player: Player | None = None

        self.sprite = Sprite.from_atlas("atlas.png", "key")
        self.text = Text("fonts/m5x7.16.png")
        self.text.text = "x 0"
        self.keys = 0

        self.sprite_position = Point(9, 32)
        self.text_position = Point(20, 30)

    def start(self) -> None:
        self.player = self.find("Player")

    def update(self) -> None:
        if keys := self.player.keys:
            if keys != self.keys:
                self.keys = keys
                self.text.text = f"x {self.keys}"

    def draw(self, camera: Camera) -> None:
        self.sprite.draw(camera, self.sprite_position)
        self.text.draw(camera, self.text_position)
