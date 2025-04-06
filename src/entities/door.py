from __future__ import annotations

from potion import *

if TYPE_CHECKING:
    from entities.player import Player


class Door(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.tags.add("Door")

        self.player: Player | None = None

        self.sprite = AnimatedSprite.from_atlas("atlas.png", "door")
        self.sprite.play("Closed")
        self.sprite.get_animation("Open").loop = False

        self.locked = True

        self.collisions_enabled = True
        self.solid = True
        self.width = 16
        self.height = 24

    def start(self) -> None:
        self.player = self.find("Player")

    def update(self) -> None:
        self.sprite.update()

        if not self.locked:
            if not self.sprite.is_playing:
                self.collisions_enabled = False

    def draw(self, camera: Camera) -> None:
        self.sprite.draw(camera, self.position())

    def on_collision_begin(self, other: Entity) -> None:
        if self.locked:
            if other.name == "Player":
                if self.player.keys:
                    self.player.keys -= 1
                    self.unlock()

    def unlock(self) -> None:
        if not self.locked:
            return

        self.locked = False
        self.sprite.play("Open")
