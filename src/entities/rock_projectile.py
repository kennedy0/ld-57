from potion import *

from entities.rock_projectile_fx import RockProjectileFx


class RockProjectile(Entity):
    def __init__(self) -> None:
        super().__init__()

        self.sprite_red = AnimatedSprite.from_atlas("atlas.png", "rock_projectile_red")
        self.sprite_red.play("default")

        self.sprite_green = AnimatedSprite.from_atlas("atlas.png", "rock_projectile_green")
        self.sprite_green.play("default")

        self.reflected = False

        self.collisions_enabled = True
        self.width = 4
        self.height = 4

        self.speed = 1
        self.direction = 0

        self.offset = Point(2, 2)

        self.timer = 600

    def update(self) -> None:
        self.sprite_red.update()
        self.sprite_green.update()

        self.timer -= 1
        if self.timer <= 0:
            self.destroy()
            self.rock_fx()

    def reflect(self) ->  None:
        self.reflected = True
        self.direction *= -1

    def draw(self, camera: Camera) -> None:
        if self.reflected:
            self.sprite_green.draw(camera, self.position() - self.offset)
        else:
            self.sprite_red.draw(camera, self.position() - self.offset)

    def on_collision_begin(self, other: Entity) -> None:
        if not self.reflected and other.name == "Player":
            try:
                other.damage()
                self.destroy()
                self.rock_fx()
            except:
                pass
        elif self.reflected and "Enemy" in other.tags:
            try:
                other.damage()
                self.destroy()
                self.rock_fx()
            except:
                pass
        elif other.solid:
            self.destroy()
            self.rock_fx()

    def rock_fx(self) -> None:
        for _ in range(3):
            fx = RockProjectileFx.instantiate()
