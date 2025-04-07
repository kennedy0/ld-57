from __future__ import annotations

from potion import *

if TYPE_CHECKING:
    from entities.player import Player
    from entities.game_manager import GameManager


class Boss(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.name = "Boss"
        self.pausable = False
        self.game_over = False
        self.game_over_started = False
        self.game_over_gravity = False

        self.player: Player | None = None
        self.game_manager: GameManager | None = None

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

        self.state = "Idle"

        self.fly_timer = 0
        self.fly_timer_max = 60

        self.move_speed = .5
        self.player_direction = 0
        self.x_distance_to_player = 0

        self.start_y = 0
        self.dy = 0

        self.death_sfx = SoundEffect("sfx/boss_death.wav")
        self.butt_sfx = SoundEffect("sfx/butt.wav")
        self.block_sfx = SoundEffect("sfx/brick_break.wav")
        self.jump_sfx = SoundEffect("sfx/boss_jump.wav")

    def start(self) -> None:
        self.start_y = self.y
        self.player = self.find("Player")
        self.game_manager = self.find("GameManager")

    def update(self) -> None:
        self.sprite.update()

        if self.player.x < self.bbox().center().x:
            self.player_direction = -1
        else:
            self.player_direction = 1

        if self.game_over:
            if not self.game_over_started:
                self.game_over_started = True
                self.state = "Fly"
                self.sprite.play("Fly")
                self.fly_timer = self.fly_timer_max
                self.solid = False
                self.collisions_enabled = False

        if self.state == "Idle":
            if self.sprite.animation == "Idle" and not self.sprite.is_playing:
                self.state = "Jump"
                self.sprite.play("BeforeJump")
                return
        elif self.state == "Jump":
            if self.sprite.animation == "BeforeJump" and not self.sprite.is_playing:
                self.sprite.play("Jump")
                self.jump_sfx.play()
                return
            elif self.sprite.animation == "Jump" and not self.sprite.is_playing:
                self.state = "Fly"
                self.sprite.play("Fly")
                self.fly_timer = self.fly_timer_max
                return
        elif self.state == "Fly":
            self.y = self.start_y
            self.face_player()
            self.fly_timer -= 1
            if self.fly_timer <= 0:
                self.fly_timer = 0
            if self.fly_timer == 0:
                self.x_distance_to_player = abs(self.bbox().center().x - self.player.bbox().center().x)
                if not self.game_over:
                    self.move_x(self.move_speed * self.player_direction)
                if self.x_distance_to_player < 16:
                    self.sprite.play("Slam")
                    self.state = "Slam"
                    return
                if self.game_over:
                    if self.find("Bridge"):
                        pass
                    else:
                        self.sprite.play("Slam")
                        self.state = "Slam"
                        self.game_over_gravity = True
                        return
        elif self.state == "Slam":
            if self.game_over:
                if self.sprite.animation == "Slam" and self.sprite.frame_started(3):
                    self.sprite.pause()
            if self.sprite.animation == "Slam" and self.sprite.frame_started(4):
                self.break_blocks()
                if self.player.bbox().intersects_rect(self.bbox()):
                    self.player.damage()
            if self.sprite.animation == "Slam" and not self.sprite.is_playing:
                self.state = "Idle"
                self.sprite.play("Idle")
                self.face_player()
                return

        if self.game_over:
            if self.game_over_gravity:
                self.dy += .1
                self.move_y(self.dy)
        else:
            self.snap_to_ground()

        if self.game_over:
            if self.y > 200:
                self.destroy()
                self.death_sfx.play()
                self.game_manager.end_game()
                Music.stop()

    def face_player(self) -> None:
        if self.player_direction > 0:
            self.sprite.flip_horizontal = True
        else:
            self.sprite.flip_horizontal = False

    def foot_rect(self) -> Rect:
        return Rect(self.x, self.bbox().bottom(), self.width, 2)

    def break_blocks(self) -> None:
        self.block_sfx.play()
        self.butt_sfx.play()
        foot_rect = self.foot_rect()
        for entity in self.scene.entities.active_entities():
            if "CrackedBlock" in entity.tags:
                if entity.bbox().intersects_rect(foot_rect):
                    try:
                        entity.damage()
                    except:
                        pass

    def snap_to_ground(self) -> None:
        self.move_y(32)

    def draw(self, camera: Camera) -> None:
        self.sprite.draw(camera, self.position() + self.sprite_offset)

    def debug_draw(self, camera: Camera) -> None:
        self.bbox().draw(camera, Color.red())
