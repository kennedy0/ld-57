from potion import *


class Sword(Entity):
    def __init__(self) -> None:
        super().__init__()

        self.sprite = AnimatedSprite.from_atlas("atlas.png", "sword")
        self.sprite.play("default")
        self.sprite.get_animation("default").loop = False

        self.collisions_enabled = True
        self.width = 15
        self.height = 2

        self.dx = 2
        self.dy = 2
        self.gravity = .3

    def update(self) -> None:
        self.sprite.update()
        self.move(self.x, self.y)
        if not self.sprite.is_playing:
            self.destroy()

    def draw(self, camera: Camera) -> None:
        self.sprite.draw(camera, self.position() + Point(0, -3))

    def on_collision_begin(self, other: Entity) -> None:
        if "Enemy" in other.tags:
            try:
                other.damage()
                self.collisions_enabled = False
            except:
                Log.warning(f"{other.name} has no damage() method")
