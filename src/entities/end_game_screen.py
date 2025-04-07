from potion import *


class EndGameScreen(Entity):
    def __init__(self) -> None:
        super().__init__()

        self.sprite_1 = Sprite.from_atlas("atlas.png", "end_screen_1")
        self.sprite_2 = Sprite.from_atlas("atlas.png", "end_screen_2")

        self.timer = -120

    def update(self) -> None:
        self.timer += 1
        if self.timer >= 255:
            self.timer = 255

        self.sprite_2.opacity = self.timer

    def draw(self, camera: Camera) -> None:
        self.sprite_1.draw(camera, self.position())
        self.sprite_2.draw(camera, self.position())
