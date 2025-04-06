from potion import *


class Bonfire(Entity):
    def __init__(self) -> None:
        super().__init__()

        self.sprite = AnimatedSprite.from_atlas("atlas.png", "bonfire")
        self.sprite.play("Idle")

        self.sprite.get_animation("Lit").loop = False

        self.lit = False

        self.collisions_enabled = True
        self.width = 24
        self.height = 32

    def update(self) -> None:
        self.sprite.update()

        if self.sprite.animation == "Lit" and not self.sprite.is_playing:
            self.sprite.play("Burning")

    def draw(self, camera: Camera) -> None:
        self.sprite.draw(camera, self.position())

    def on_collision_begin(self, other: Entity) -> None:
        if not self.lit:
            if other.name == "Player":
                self.sprite.play("Lit")
                self.lit = True
