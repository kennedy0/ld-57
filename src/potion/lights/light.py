from potion.camera import Camera
from potion.data_types.blend_mode import BlendMode
from potion.data_types.point import Point
from potion.lights.base_light import BaseLight
from potion.log import Log
from potion.sprite import Sprite


class Light(BaseLight):
    """ A light that uses sprites to cast lights. """
    def __init__(self) -> None:
        super().__init__()
        self._light_sprite: Sprite = Sprite.empty()
        self._glow_sprite: Sprite = Sprite.empty()

    @property
    def light_sprite(self) -> Sprite:
        """ The lighting pass sprite. """
        return self._light_sprite

    @light_sprite.setter
    def light_sprite(self, value: Sprite) -> None:
        self._light_sprite = value

        if __debug__:
            self._check_sprites_for_errors()

    @property
    def glow_sprite(self) -> Sprite:
        """ The glow pass sprite. """
        return self._glow_sprite

    @glow_sprite.setter
    def glow_sprite(self, value: Sprite) -> None:
        self._glow_sprite = value

        if __debug__:
            self._check_sprites_for_errors()

    def draw(self, camera: Camera, position: Point) -> None:
        if self._light_sprite:
            with camera.render_pass("Lighting"):
                self._light_sprite.color = self.color
                self._light_sprite.opacity = int(self.intensity * 255)
                self._light_sprite.draw(camera, position)

        if self._glow_sprite:
            with camera.render_pass("Glow"):
                self._glow_sprite.color = self.color
                self._glow_sprite.opacity = int(self.glow_intensity * 255)
                self._glow_sprite.draw(camera, position)

    def _check_sprites_for_errors(self) -> None:
        """ Check the light and glow sprites for errors. """
        if self._light_sprite:
            if self._light_sprite.texture.blend_mode != BlendMode.ADD:
                Log.warning(f"{self} is using {self._light_sprite} with a texture blend mode of "
                            f"{self._light_sprite.texture.blend_mode}; expected {BlendMode.ADD}")

        if self.glow_sprite:
            if self._glow_sprite.texture.blend_mode != BlendMode.ADD:
                Log.warning(f"{self} is using {self._glow_sprite} with a texture blend mode of "
                            f"{self._glow_sprite.texture.blend_mode}; expected {BlendMode.ADD}")

        if self._light_sprite and self._glow_sprite:
            if self._light_sprite == self._glow_sprite:
                Log.warning(f"{self} is using {self._light_sprite} for both the sprite and glow sprite; a separate "
                            f"sprite should be created for each")
