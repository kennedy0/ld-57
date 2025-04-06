from __future__ import annotations

from potion import *

if TYPE_CHECKING:
    from entities.player import Player


class RupeeUi(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.tags.add("UI")

        self.player: Player | None = None

        self.sprite = Sprite.from_atlas("atlas.png", "rupee")
        self.text = Text("fonts/m5x7.16.png")
        self.text.text = "x 00"
        self.rupees = 0

        self.sprite_position = Point(10, 20)
        self.text_position = Point(20, 20)

    def start(self) -> None:
        self.player = self.find("Player")

    def update(self) -> None:
        if rupees := self.player.rupees:
            if rupees != self.rupees:
                self.rupees = rupees
                self.text.text = f"x {self.rupees:02d}"

    def draw(self, camera: Camera) -> None:
        self.sprite.draw(camera, self.sprite_position)
        self.text.draw(camera, self.text_position)
