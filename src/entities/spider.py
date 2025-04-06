from potion import *


class Spider(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.tags.add("Enemy")
        self.x_direction = 1
        self.delay = 0


        self.sprite = AnimatedSprite.from_atlas("atlas.png", "spider")
        self.sprite.play("default")

        self.timer = self.delay
        self.waiting = True

        self.collisions_enabled = True
        self.solid = False
        self.width = 8
        self.height = 8

        self.speed = 1

    def awake(self) -> None:
        self.timer = self.delay

    def update(self) -> None:
        self.sprite.update()

        self.timer -= 1
        if self.timer <= 0:
            self.waiting = False

        if self.waiting:
            return

        self.move(self.x + (self.speed * self.x_direction), self.y)

    def draw(self, camera: Camera) -> None:
        self.sprite.draw(camera, self.position())

    def debug_draw(self, camera: Camera) -> None:
        self.bbox().draw(camera, Color.red())
