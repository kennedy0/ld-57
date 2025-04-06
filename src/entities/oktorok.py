from potion import *

from entities.enemy import Enemy
from entities.score_fx import ScoreFx
from entities.player_death_fx import PlayerDeathFx
from entities.rock_projectile import RockProjectile


class Oktorok(Enemy):
    def __init__(self) -> None:
        super().__init__()

        self.player: Entity | None = None

        self.sprite = AnimatedSprite.from_atlas("atlas.png", "oktorok")
        self.sprite.play("Idle")

        self.sprite.get_animation("Attack").loop = False

        self.facing_left = False
        self.range = 8

        self.collisions_enabled = True
        self.width = 10
        self.height = 9

        self.detect_player_rect = Rect.empty()
        self.player_in_range = False

    def start(self) -> None:
        self.player = self.find("Player")

        if self.facing_left:
            self.detect_player_rect = Rect(self.bbox().left() - self.range, self.bbox().top(), self.range, 8)
        else:
            self.sprite.flip_horizontal = True
            self.detect_player_rect = Rect(self.bbox().right() + 1, self.bbox().top(), self.range, 8)

    def on_death(self) -> None:
        fx = PlayerDeathFx.instantiate()
        fx.set_position(self.bbox().center())
        fx.sprite.color = Color.from_hex("#6a3771")

    def update(self) -> None:
        if self.player.bbox().intersects_rect(self.detect_player_rect):
            self.player_in_range = True
        else:
            self.player_in_range = False

        if self.player_in_range:
            self.sprite.play("Attack")
            if self.sprite.frame_started(2):
                self.shoot_projectile()
        else:
            self.sprite.play("Idle")

        self.sprite.update()

    def shoot_projectile(self) -> None:
        projectile = RockProjectile.instantiate()
        if self.facing_left:
            projectile.direction = -1
        else:
            projectile.direction = 11

    def draw(self, camera: Camera) -> None:
        self.sprite.draw(camera, self.position() - Point(1, 1))
        self.detect_player_rect.draw(camera, Color.red())
