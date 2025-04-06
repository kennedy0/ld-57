from __future__ import annotations

from potion import *

if TYPE_CHECKING:
    from entities.player import Player


class HeartsUi(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.tags.add("UI")

        self.player: Player | None = None

        self.sprite_full = Sprite.from_atlas("atlas.png", "heart_full")
        self.sprite_empty = Sprite.from_atlas("atlas.png", "heart_empty")

        self.sprite_positions = (
            Point(10, 10),
            Point(20, 10),
            Point(30, 10),
        )

    def start(self) -> None:
        self.player = self.find("Player")

    def draw(self, camera: Camera) -> None:
        for i, p in enumerate(self.sprite_positions):
            if self.player.hp > i:
                self.sprite_full.draw(camera, p)
            else:
                self.sprite_empty.draw(camera, p)
