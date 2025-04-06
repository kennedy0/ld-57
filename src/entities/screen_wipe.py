from potion import *

class ScreenWipe(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.name = "ScreenWipe"
        self.tags.add("UI")

        self.sprite = Sprite("images/screen_wipe.png")
        self.pausable = False

        self.scene_start = True
        self.is_transitioning = False
        self.is_hiding = False
        self.timer = 0
        self.timer_max = 100

        self.from_y = 0
        self.to_y = 0

        self.z = -9999

    def update(self) -> None:
        if self.is_transitioning:
            self.timer -= 1
            if self.timer <= 0:
                self.is_transitioning = False
                self.y = self.to_y
            else:
                t = (self.timer_max - self.timer) / self.timer_max
                y = pmath.lerp(self.from_y, self.to_y, t)
                self.y = int(y)

    def hide(self) -> None:
        if self.is_transitioning:
            return

        self.is_transitioning = True
        self.is_hiding = True
        self.scene_start = False
        self.timer = self.timer_max
        self.from_y = self.sprite.height()
        self.to_y = Renderer.resolution()[1] - self.sprite.height()
        self.sprite.flip_vertical = True

    def show(self) -> None:
        if self.is_transitioning:
            return

        self.is_transitioning = True
        self.is_hiding = False
        self.scene_start = False
        self.timer = self.timer_max
        self.from_y = 0
        self.to_y = self.sprite.height() * -1
        self.sprite.flip_vertical = False

    def draw(self, camera: Camera) -> None:
        if self.scene_start or self.is_transitioning or self.is_hiding:
            self.sprite.draw(camera, self.position())
