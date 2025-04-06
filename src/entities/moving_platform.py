import math

from potion import *


class MovingPlatform(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.tags.add("Platform")
        self.tags.add("MovingPlatform")

        self.sprite = Sprite.from_atlas("atlas.png", "mario_platform")
        self.carrying: Entity | None = None

        self.collisions_enabled = True
        self.width = 32
        self.height = 8

        self.anchor_point = Point.zero()
        self.cycle_time = 60  # A good default is `y_distance` * 2.5
        self.y_distance = 24
        self.x_distance = 0

        self.frame = 0

    def awake(self) -> None:
        self.anchor_point = self.position()
        self.visible = False

    def on_activate(self) -> None:
        self.frame = 0
        self.visible = False

    def on_deactivate(self) -> None:
        self.frame = 0

    def update(self) -> None:
        t = self.frame / self.cycle_time
        x = int(math.sin(t) * self.x_distance)
        y = int(math.sin(t) * self.y_distance)
        self.set_position(self.anchor_point + Point(x, y))

        if self.carrying:
            self.carrying.y = self.y - self.carrying.height

        self.frame += 1
        self.visible = True

    def draw(self, camera: Camera) -> None:
        if self.visible:
            self.sprite.draw(camera, self.position())
