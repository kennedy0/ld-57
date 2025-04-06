from potion import *


class ShopFire(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.tags.add("Enemy")
        self.sprite = AnimatedSprite.from_atlas("atlas.png", "shop_fire")
        self.sprite.play("default")

        self.collisions_enabled = True
        self.width = 8
        self.height = 8

    def damage(self) -> None:
        pass

    def update(self) -> None:
        self.sprite.update()

    def draw(self, camera: Camera) -> None:
        self.sprite.draw(camera, self.position())
