from __future__ import annotations

from potion import *

if TYPE_CHECKING:
    from entities.player import Player


class UndertaleUi(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.tags.add("UI")

        self.player: Player | None = None

        self.text = Text("fonts/m5x7.16.png")
        self.text.text = f"HP 10/10"

        self.text_position = Point(6, 6)

    def start(self) -> None:
        self.player = self.find("Player")
        self.text.text = f"HP {self.player.max_hp}/{self.player.max_hp}"

    def update(self) -> None:
        if hp := self.player.hp:
            self.text.text = f"HP {hp:02d}/{self.player.max_hp:02d}"

    def draw(self, camera: Camera) -> None:
        self.text.draw(camera, self.text_position)
