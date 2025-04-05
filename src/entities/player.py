from __future__ import annotations

from potion import *


class Player(Entity):
    def __init__(self) -> None:
        super().__init__()

        # Sprites
        self.body_sprite = AnimatedSprite.from_atlas("atlas.png", "player_body")
        self.body_outline_sprite = AnimatedSprite.from_atlas("atlas.png", "player_body_outline")

        self.head_sprite = AnimatedSprite.from_atlas("atlas.png", "player_head")
        self.head_outline_sprite = AnimatedSprite.from_atlas("atlas.png", "player_head_outline")

        self.hands_sprite = AnimatedSprite.from_atlas("atlas.png", "player_hands")
        self.hands_outline_sprite = AnimatedSprite.from_atlas("atlas.png", "player_hands_outline")

        # Collision
        self.collisions_enabled = True
        self.solid = False
        self.width = 10
        self.height = 15

        # Movement
        self.move_speed = 1
        self.gravity = .2
        self.jump_force = 3

        # Input
        self.input_x = 0
        self.jump = False
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

    def awake(self) -> None:
        for sprite in self.sprites():
            sprite.get_animation("Idle").loop = False
            sprite.get_animation("Jump").loop = False
            sprite.get_animation("Hang").loop = False
            sprite.get_animation("Fall").loop = False
            sprite.get_animation("Land").loop = False

    def sprites(self) -> Generator[AnimatedSprite]:
        yield self.body_sprite
        yield self.body_outline_sprite
        yield self.head_sprite
        yield self.head_outline_sprite
        yield self.hands_sprite
        yield self.hands_outline_sprite

    def grounded_rect(self) -> Rect:
        return Rect(self.x, self.y + self.height, self.width, 1)

    def head_hit_rect(self) -> Rect:
        return Rect(self.x, self.y - 1, self.width, 1)

    def update(self) -> None:
        self.update_input()
        self.update_physics()
        self.update_state()
        self.update_animation()
        for sprite in self.sprites():
            sprite.update()

    def update_input(self) -> None:
        # Left / Right Input
        self.input_x = 0
        if Input.get_button("Left"):
            self.input_x = -1
            for sprite in self.sprites():
                sprite.flip_horizontal = True
        elif Input.get_button("Right"):
            self.input_x = 1
            for sprite in self.sprites():
                sprite.flip_horizontal = False

        # Jump
        if Input.get_button_down("Jump") and self.grounded:
            self.jump = True
        elif Input.get_button_up("Jump") or not self.grounded:
            self.jump = False

    def update_physics(self) -> None:
        # Horizontal movement
        self.dx = self.input_x * self.move_speed

        # Vertical movement
        if self.grounded:
            self.dy = 0
            if self.jump:
                self.dy -= self.jump_force
        else:
            if self.dy < 0 and self.head_hit:
                self.dy = 0
            else:
                self.dy += self.gravity

        # Move
        self.move_x(self.dx)
        self.move_y(self.dy)

        # Check foot and head collisions
        self.grounded_last_frame = self.grounded
        self.grounded = False
        self.head_hit = False
        for entity in self.scene.entities:
            if entity == self:
                continue
            if entity.solid:
                if entity.intersects(self.grounded_rect()):
                    self.grounded = True
                if entity.intersects(self.head_hit_rect()):
                    self.head_hit = True

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
        animation = self.body_sprite.animation
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
            if animation == "Idle" and self.body_sprite.get_animation("Land").is_playing:
                # If the "Land" animation is playing, let it finish before idling
                pass
            else:
                for sprite in self.sprites():
                    sprite.play(animation)

    def draw(self, camera: Camera) -> None:
        sprite_position = Point(self.x - 3, self.y - 1)
        for sprite in self.sprites():
            sprite.draw(camera, sprite_position)

    def debug_draw(self, camera: Camera) -> None:
        self.bbox().draw(camera, Color.white())
