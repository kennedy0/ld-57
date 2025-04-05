from __future__ import annotations

from potion import *

from entities.sword import Sword
from entities.player_death_fx import PlayerDeathFx

if TYPE_CHECKING:
    from entities.game_manager import GameManager


class Player(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.name = "Player"

        # References
        self.game_manager: GameManager | None = None

        # Character
        self.character = ""

        # Sprites
        self.body_sprite = AnimatedSprite.from_atlas("atlas.png", "player_body")
        self.body_outline_sprite = AnimatedSprite.from_atlas("atlas.png", "player_body_outline")

        self.head_sprite = AnimatedSprite.from_atlas("atlas.png", "player_head")
        self.head_outline_sprite = AnimatedSprite.from_atlas("atlas.png", "player_head_outline")

        self.hands_sprite = AnimatedSprite.from_atlas("atlas.png", "player_hands")
        self.hands_outline_sprite = AnimatedSprite.from_atlas("atlas.png", "player_hands_outline")

        # Character heads
        self.head_outline_sprite_normal = AnimatedSprite.from_atlas("atlas.png", "player_head_outline")
        self.head_outline_sprite_mario = AnimatedSprite.from_atlas("atlas.png", "player_head_outline_mario")
        self.head_outline_sprite_link = AnimatedSprite.from_atlas("atlas.png", "player_head_outline_link")

        # Item Sprite
        self.item_sprite: Sprite | None = None

        # Special Sprite
        self.special_sprite: AnimatedSprite | None = None

        # Special
        self.special_cooldown_timer = 0
        self.special_stun_timer = 0

        # Held item
        self.item: Entity | None = None

        # Collision
        self.collisions_enabled = True
        self.solid = False
        self.width = 10
        self.height = 15

        # Movement
        self.move_speed = 1
        self.gravity = .2
        self.terminal_velocity = 4
        self.jump_force = 3.75
        self.coyote_timer = 0
        self.coyote_timer_max = 8
        self.early_jump_timer = 0
        self.early_jump_timer_max = 8
        self.gravity_enabled = True
        self.riding: Entity | None = None

        # Input
        self.facing_x = 1
        self.input_x = 0
        self.jump = False
        self.jump_release = False
        self.special = False

        # Physics
        self.grounded = False
        self.grounded_last_frame = False
        self.head_hit = False
        self.dx = 0
        self.dy = 0

        # State
        self.state = "Idle"
        self.state_changed = False

        # HP
        self.hp = 1
        self.max_hp = 1
        self.invincibility_timer = 0

        # Start
        self.scene_start = True

    def awake(self) -> None:
        # Init defaults
        self.max_hp = 1
        self.x = 160 - self.width // 2
        self.y =- 20
        self.z = -1

        # Initialize player attributes based on the scene name
        match self.scene.name:
            case "mario_world":
                self.x = 32
                self.set_character("Mario")
            case _:
                Log.warning(f"No Player initialization for scene '{self.scene.name}'")

        # Init HP
        self.hp = self.max_hp

        # Init Sprites
        self.init_sprites()

    def start(self) -> None:
        self.game_manager = self.find("GameManager")

    def init_sprites(self) -> None:
        for sprite in self.sprites():
            sprite.get_animation("Idle").loop = False
            sprite.get_animation("Jump").loop = False
            sprite.get_animation("Hang").loop = False
            sprite.get_animation("Fall").loop = False
            sprite.get_animation("Land").loop = False
            sprite.get_animation("Land").set_duration(100)
            if self.facing_x > 0:
                sprite.flip_horizontal = False
            elif self.facing_x < 0:
                sprite.flip_horizontal = True

    def animation_name(self) -> str:
        return self.body_sprite.animation

    def animation_frame(self) -> int:
        return self.body_sprite.frame

    def get_sprite_color(self) -> Color | None:
        return self.body_outline_sprite.color

    def get_animation(self, name: str) -> Animation | None:
        return self.body_sprite.get_animation(name)

    def sprites(self) -> Generator[AnimatedSprite]:
        yield self.body_sprite
        yield self.body_outline_sprite
        yield self.head_sprite
        yield self.head_outline_sprite
        yield self.hands_sprite
        yield self.hands_outline_sprite

    def outline_sprites(self) -> Generator[AnimatedSprite]:
        yield self.body_outline_sprite
        yield self.head_outline_sprite
        yield self.hands_outline_sprite

    def hand_offset(self) -> Point:
        if self.animation_name() == "Idle":
            p = Point(4, 12)
        elif self.animation_name() == "Run":
            if self.animation_frame() == 1:
                p = Point(11, 9)
            elif self.animation_frame() == 2:
                p = Point(10, 10)
            elif self.animation_frame() == 3:
                p = Point(4, 11)
            elif self.animation_frame() == 4:
                p = Point(3, 10)
            elif self.animation_frame() == 5:
                p = Point(2, 9)
            elif self.animation_frame() == 6:
                p = Point(2, 10)
            elif self.animation_frame() == 7:
                p = Point(4, 11)
            elif self.animation_frame() == 8:
                p = Point(8, 10)
            else:
                p = Point.zero()
        elif self.animation_name() == "Jump":
            p = Point(3, 10)
        elif self.animation_name() == "Hang":
            p = Point(3, 9)
        elif self.animation_name() == "Fall":
            p = Point(4, 8)
        elif self.animation_name() == "Land":
            p = Point(3, 11)
        else:
            p = Point.zero()

        return p

    def grounded_rect(self) -> Rect:
        return Rect(self.x, self.y + self.height, self.width, 1)

    def head_hit_rect(self) -> Rect:
        return Rect(self.x, self.y - 1, self.width, 1)

    def set_character(self, character: str) -> None:
        self.character = character

        if character == "Mario":
            self.head_outline_sprite = self.head_outline_sprite_mario
            for sprite in self.outline_sprites():
                sprite.color = Color.from_hex("#c92464")
        elif character == "Link":
            self.head_outline_sprite = self.head_outline_sprite_link
            for sprite in self.outline_sprites():
                sprite.color = Color.from_hex("#1e8875")
        elif character == "":
            self.head_outline_sprite = self.head_outline_sprite_normal
            self.item_sprite = None
            self.special_sprite = None
            for sprite in self.outline_sprites():
                sprite.color = None
        else:
            Log.warning(f"Character '{character}' does not exist, removing character")
            self.set_character("")
            return

        self.init_sprites()

    def update(self) -> None:
        if __debug__:
            self._debug_input()

        self.update_timers()
        self.update_input()
        self.update_physics()
        self.update_special()
        self.update_state()
        self.update_animation()
        self.update_item_position()
        for sprite in self.sprites():
            sprite.update()

    def update_timers(self) -> None:
        self.early_jump_timer -= 1
        if self.early_jump_timer <= 0:
            self.early_jump_timer = 0

        self.coyote_timer -= 1
        if self.coyote_timer <= 0:
            self.coyote_timer = 0

        self.special_cooldown_timer -= 1
        if self.special_cooldown_timer <= 0:
            self.special_cooldown_timer = 0

        self.special_stun_timer -= 1
        if self.special_stun_timer <= 0:
            self.special_stun_timer = 0
            if self.character == "Link":
                self.gravity_enabled = True

        self.invincibility_timer -= 1
        if self.invincibility_timer <= 0:
            self.invincibility_timer = 0

    def reset_timers(self) -> None:
        self.early_jump_timer = 0
        self.coyote_timer = 0
        self.special_cooldown_timer = 0
        self.special_stun_timer = 0
        self.invincibility_timer = 0

    def update_input(self) -> None:
        if self.scene_start:
            return

        # Left / Right Input
        self.input_x = 0
        if self.special_stun_timer <= 0:
            if Input.get_button("Left"):
                self.input_x = -1
                for sprite in self.sprites():
                    sprite.flip_horizontal = True
                    self.facing_x = -1
            elif Input.get_button("Right"):
                self.input_x = 1
                for sprite in self.sprites():
                    sprite.flip_horizontal = False
                    self.facing_x = 1

        # Jump
        self.jump = False
        if self.special_stun_timer <= 0:
            if Input.get_button_down("Jump"):
                self.early_jump_timer = self.early_jump_timer_max
                self.jump = True
            elif self.early_jump_timer:
                self.jump = True

        # Jump release
        self.jump_release = False
        if Input.get_button_up("Jump"):
            self.jump_release = True

        # Special
        self.special = False
        if Input.get_button_down("Special") and self.special_stun_timer <= 0:
            self.special = True

    def update_physics(self) -> None:
        # Horizontal movement
        self.dx = self.input_x * self.move_speed

        # Vertical movement
        if self.jump and self.coyote_timer:
            self.dy = -self.jump_force
            self.coyote_timer = 0
        elif self.grounded:
            self.dy = 0
            self.coyote_timer = self.coyote_timer_max
        else:
            if self.jump_release and self.dy < 0:
                self.dy /= 1.8

            if self.dy < 0 and self.head_hit:
                self.dy = 0
            else:
                self.dy += self.gravity

        if self.dy > self.terminal_velocity:
            self.dy = self.terminal_velocity

        if not self.gravity_enabled:
            self.dx = 0
            self.dy = 0

        # Move
        self.move_x(self.dx)
        self.move_y(self.dy)

        # Check foot and head collisions
        self.grounded_last_frame = self.grounded
        self.grounded = False
        self.head_hit = False
        if self.riding:
            try:
                self.riding.carrying = None
            except:
                pass
            self.riding = None
        for entity in self.scene.entities.active_entities():
            if entity == self:
                continue
            if entity.solid:
                if entity.intersects(self.grounded_rect()):
                    self.grounded = True
                if entity.intersects(self.head_hit_rect()):
                    self.head_hit = True
                    if hasattr(entity, "on_head_hit"):
                        entity.on_head_hit()
            elif "Platform" in entity.tags:
                if entity.intersects(self.grounded_rect()):
                    self.grounded = True
                    if "MovingPlatform" in entity.tags and not (self.jump and self.coyote_timer):
                        self.riding = entity
                        try:
                            self.riding.carrying = self
                        except:
                            pass

        # If riding an object, override the Y position
        if self.riding:
            self.grounded = True
            self.dy = 0

        # Can never go past the left side of the screen
        if self.x < 0:
            self.x = 0

        if self.y > 180:
            screen = self.x // 320
            print(screen)
            if screen == len(list(self.scene.levels)) - 1:
                Log.warning("IMPLEMENT LEVEL TRANSITION")
            else:
                self.force_kill()

        # Give player control when they're grounded
        if self.grounded:
            self.scene_start = False

    def update_special(self) -> None:
        if self.special:
            if self.character == "Mario":
                pass
                # if self.special_cooldown_timer == 0:
                #     self.special_cooldown_timer = 30
                #     fireball = Fireball.instantiate()
                #     if self.facing_x < 0:
                #         fireball.set_position(self.position() + Point(-7, 5))
                #         fireball.dx *= -1
                #     else:
                #         fireball.set_position(self.position() + Point(10, 5))
            elif self.character == "Link":
                if self.special_cooldown_timer == 0:
                    self.gravity_enabled = False
                    self.special_cooldown_timer = 20
                    self.special_stun_timer = 10
                    sword = Sword.instantiate()
                    if self.facing_x < 0:
                        sword.set_position(self.position() + Point(-16, 10))
                        sword.sprite.flip_horizontal = True
                    else:
                        sword.set_position(self.position() + Point(10, 10))

    def update_state(self) -> None:
        if not self.grounded:
            if self.dy < 0:
                state = "Jumping"
            else:
                state = "Falling"
        else:
            if self.input_x:
                state = "Running"
            else:
                state = "Idle"

        if state != self.state:
            self.state = state
            self.state_changed = True
        else:
            self.state_changed = False

    def update_animation(self) -> None:
        # Get the animation to play
        animation = self.animation_name()
        if self.state == "Idle":
            if not self.grounded_last_frame and self.grounded:
                animation = "Land"
            else:
                animation = "Idle"
        elif self.state == "Running":
            animation = "Run"
        elif self.state in ("Jumping", "Falling"):
            if abs(self.dy) < 1:
                animation = "Hang"
            elif self.state == "Jumping":
                animation = "Jump"
            elif self.state == "Falling":
                animation = "Fall"

        # Play the animation if it's new
        if animation != self.body_sprite.animation:
            if animation == "Idle" and self.get_animation("Land").is_playing:
                # If the "Land" animation is playing, let it finish before idling
                pass
            else:
                for sprite in self.sprites():
                    sprite.play(animation)

    def update_item_position(self) -> None:
        if self.item:
            self.item.set_position(self.position() + self.hand_offset())

    def draw(self, camera: Camera) -> None:
        sprite_position = Point(self.x - 3, self.y - 1)

        self.body_sprite.draw(camera, sprite_position)
        self.body_outline_sprite.draw(camera, sprite_position)
        self.head_sprite.draw(camera, sprite_position)
        self.head_outline_sprite.draw(camera, sprite_position)

        if self.item_sprite:
            self.item_sprite.draw(camera, sprite_position + self.hand_offset())

        self.hands_sprite.draw(camera, sprite_position)
        self.hands_outline_sprite.draw(camera, sprite_position)

    def debug_draw(self, camera: Camera) -> None:
        # self.bbox().draw(camera, Color.white())
        # if self.head_hit:
        #     self.head_hit_rect().draw(camera, Color.green())
        # else:
        #     self.head_hit_rect().draw(camera, Color(0, 100, 0, 255))
        # if self.grounded:
        #     self.grounded_rect().draw(camera, Color.red())
        # else:
        #     self.grounded_rect().draw(camera, Color(100, 0, 0, 255))
        (self.position() + self.hand_offset()).draw(camera, Color.red())

    def on_collision_begin(self, other: Entity) -> None:
        if "Enemy" in other.tags:
            if self.invincibility_timer:
                pass
            elif self.character == "Mario" and self.bbox().bottom() <= other.bbox().top():
                if Input.get_button("Jump"):
                    self.dy = self.jump_force * -1
                else:
                    self.dy = (self.jump_force / 2) * -1
                try:
                    other.damage()
                except:
                    Log.warning(f"{other.name} has no damage() method")
            else:
                self.damage()
        elif "Coin" in other.tags:
            other.on_collect()

    def damage(self) -> None:
        self.hp -= 1
        self.invincibility_timer = 60
        if self.hp <= 0:
            self.on_death()

    def force_kill(self) -> None:
        self.hp = 0
        self.on_death()

    def on_death(self) -> None:
        fx = PlayerDeathFx.instantiate()
        fx.set_position(self.bbox().center())
        fx.sprite.color = self.get_sprite_color()
        self.active = False
        self.game_manager.reload_scene()

    def _debug_input(self) -> None:
        # Die
        if Keyboard.get_key_down(Keyboard.ESCAPE):
            self.force_kill()

        # Switch Character
        if Keyboard.get_key_down(Keyboard.NUM_0):
            self.set_character("")
        elif Keyboard.get_key_down(Keyboard.NUM_1):
            self.set_character("Mario")
        elif Keyboard.get_key_down(Keyboard.NUM_2):
            self.set_character("Link")
