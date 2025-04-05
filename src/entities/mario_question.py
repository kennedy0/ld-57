from potion import *

from entities.mario_coin import MarioCoin


class MarioQuestion(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.sprite = AnimatedSprite.from_atlas("atlas.png", "mario_question_on")
        self.sprite.play("default")
        self.off_sprite = AnimatedSprite.from_atlas("atlas.png", "mario_question_off")

        self.collisions_enabled = True
        self.solid = True
        self.width = 8
        self.height = 8

        self.on = True
        self.timer = 0

    def update(self) -> None:
        self.sprite.update()

        self.timer -= 1
        if self.timer <= 0:
            self.timer = 0

    def on_head_hit(self) -> None:
        if self.on:
            self.timer = 10
            self.on = False
            self.sprite = self.off_sprite
            coin = MarioCoin.instantiate()
            coin.set_position(self.position() - Point(0, 8))
            coin.timer = 15

    def draw(self, camera: Camera) -> None:
        if self.timer:
            if self.timer > 5:
                self.sprite.draw(camera, self.position() + Point(0, -2))
            else:
                self.sprite.draw(camera, self.position() + Point(0, -1))
        else:
            self.sprite.draw(camera, self.position())
