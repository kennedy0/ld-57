from __future__ import annotations

from potion import *

if TYPE_CHECKING:
    from entities.player import Player


class Boss(Entity):
    def __init__(self) -> None:
        super().__init__()

        self.player: Player | None = None

        self.sprite = AnimatedSprite.from_atlas("atlas.png", "asylum_demon")
        self.sprite.play("Idle")

        self.sprite.get_animation("Idle").loop = False
        self.sprite.get_animation("BeforeJump").loop = False
        self.sprite.get_animation("Jump").loop = False
        self.sprite.get_animation("Slam").loop = False

        self.sprite_offset = Point(-32, -32)

        self.collisions_enabled = True
        self.width = 32
        self.height = 80

        self.idle_timer = 0
        self.idle_timer_max = 120

        self.state = "Idle"

    def start(self) -> None:
        self.player = self.find("Player")

    def update(self) -> None:
        self.sprite.update()

        if self.state == "Idle":
            if self.sprite.animation == "Idle" and not self.sprite.is_playing:
                self.state = "Jump"
                self.sprite.play("BeforeJump")
                return
        elif self.state == "Jump":
            if self.sprite.animation == "BeforeJump" and not self.sprite.is_playing:
                self.sprite.play("Jump")
                return
            elif self.sprite.animation == "Jump" and not self.sprite.is_playing:
                self.state = "Fly"
                self.sprite.play("Fly")
                return
        elif self.state == "Fly":
            pass

    def draw(self, camera: Camera) -> None:
        self.sprite.draw(camera, self.position() + self.sprite_offset)

    def debug_draw(self, camera: Camera) -> None:
        self.bbox().draw(camera, Color.red())
