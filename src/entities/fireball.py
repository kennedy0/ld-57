from potion import *


class Fireball(Entity):
    def __init__(self) -> None:
        super().__init__()

        self.sprite =Sprite.from_atlas("atlas.png", "fireball")
        self.sprite.pivot.set_center()

        self.collisions_enabled = True
        self.width = 5
        self.height = 5

        self.dx = 2
        self.dy = 2
        self.gravity = .2

        self.timer = 60

    def update(self) -> None:
        self.timer -= 1
        if self.timer <= 0:
            self.destroy()
            return

        if Engine.frame() % 8 == 0:
            self.sprite.rotation += 90
            if self.sprite.rotation >= 360:
                self.sprite.rotation = 0

        self.dy += self.gravity
        self.move_y(self.dy)
        self.move_x(self.dx)

    def draw(self, camera: Camera) -> None:
        self.sprite.draw(camera, self.position() + Point(2, 2))

    def on_collision_begin(self, other: Entity) -> None:
        if "Enemy" in other.tags:
            try:
                other.damage()
                self.collisions_enabled = False
            except:
                Log.warning(f"{other.name} has no damage() method")
            self.destroy()
            return
        elif other.solid:
            if self.dy >= 0 and other.bbox().top() < self.bbox().bottom():
                self.dy = -2
            elif self.dy <= 0 and other.bbox().bottom() < self.bbox().top():
                self.dy = 1
            else:
                self.destroy()
