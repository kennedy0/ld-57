from potion import *


class ScoreFx(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.sprite = AnimatedSprite.from_atlas("atlas.png", "score_fx")
        self.sprite.pivot.set_bottom_left()
        self.sprite.get_animation("default").loop = False
        self.sprite.play("default")
        self.z = -3

    def update(self) -> None:
        self.sprite.update()
        if not self.sprite.is_playing:
            self.destroy()

        if self.sprite.frame == 2:
            self.sprite.opacity = 192
        elif self.sprite.frame == 3:
            self.sprite.opacity = 128
        elif self.sprite.frame == 4:
            self.sprite.opacity = 64

    def draw(self, camera: Camera) -> None:
        self.sprite.draw(camera, self.position())