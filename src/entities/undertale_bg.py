from potion import *


class UndertaleBg(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.name = "UndertaleBg"

        self.sprite = AnimatedSprite.from_atlas("atlas.png", "undertale_boss")
        self.sprite.play("BlinkOne")
        self.sprite.get_animation("BlinkTransition").loop = False
        self.z = 999

        self.is_transitioned = False

    def play_transition(self) -> None:
        if self.is_transitioned:
            return

        self.is_transitioned = True
        self.sprite.play("BlinkTransition")

    def update(self) -> None:
        self.sprite.update()

        if self.sprite.animation == "BlinkTransition" and not self.sprite.is_playing:
            self.sprite.play("BlinkTwo")

    def draw(self, camera: Camera) -> None:
        self.sprite.draw(camera, self.position())
