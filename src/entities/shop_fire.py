from potion import *


class ShopFire(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.sprite = AnimatedSprite.from_atlas("atlas.png", "shop_fire")
        self.sprite.play("default")

    def update(self) -> None:
        self.sprite.update()

    def draw(self, camera: Camera) -> None:
        self.sprite.draw(camera, self.position())
