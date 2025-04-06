from __future__ import annotations

from potion import *

if TYPE_CHECKING:
    from entities.player import Player


class CoinUi(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.tags.add("UI")

        self.player: Player | None = None

        self.sprite = Sprite.from_atlas("atlas.png", "coin")
        self.text = Text("fonts/m5x7.16.png")
        self.text.text = "x 00"
        self.coins = 0

        self.sprite_position = Point(10, 14)
        self.text_position = Point(20, 10)

    def start(self) -> None:
        self.player = self.find("Player")

    def update(self) -> None:
        if coins := self.player.coins:
            if coins != self.coins:
                self.coins = coins
                self.text.text = f"x {self.coins:02d}"

    def draw(self, camera: Camera) -> None:
        self.sprite.draw(camera, self.sprite_position)
        self.text.draw(camera, self.text_position)
