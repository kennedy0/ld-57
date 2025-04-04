from potion.camera import Camera
from potion.content_types.texture import Texture
from potion.data_types.blend_mode import BlendMode
from potion.data_types.color import Color
from potion.data_types.line import Line
from potion.data_types.point import Point
from potion.data_types.rect import Rect
from potion.lights.base_light import BaseLight
from potion.renderer import Renderer


class PointLight(BaseLight):
    """ A circular light centered around a point with a linear intensity falloff, and is capable of casting shadows.

    Rather than using a pre-defined sprite, this light generates its own texture by drawing pixels.
    This is an expensive operation, so it should not be done frequently or in high amounts.
    """
    def __init__(self, radius: int) -> None:
        super().__init__()
        self._radius = radius
        self._center_offset = Point(radius, radius)

        # Texture
        self._light_texture = Texture.create_target(2, 2)
        self._glow_texture = Texture.create_target(2, 2)
        self._intermediate_texture = Texture.create_target(2, 2)
        self._reset_textures()

        # Shadows
        self._cast_shadows = False

        # Callbacks
        Renderer.add_reset_callback(self._reset_textures)
        Renderer.add_resolution_change_callback(self._reset_textures)

    def __del__(self) -> None:
        Renderer.remove_reset_callback(self._reset_textures)
        Renderer.add_resolution_change_callback(self._reset_textures)

    @property
    def radius(self) -> int:
        """ The radius of the light """
        return self._radius

    @radius.setter
    def radius(self, value: int) -> None:
        if int(value) == self._radius:
            return

        self._radius = int(value)
        self._center_offset = Point(value, value)
        self._reset_textures()

    @property
    def cast_shadows(self) -> bool:
        """ Whether or not shadows are enabled. """
        return self._cast_shadows

    @cast_shadows.setter
    def cast_shadows(self, value: bool) -> None:
        self._cast_shadows = value

    def _reset_textures(self) -> None:
        width = self.radius * 2
        height = self.radius * 2

        self._light_texture = Texture.create_target(width, height)
        self._light_texture.set_blend_mode(BlendMode.ADD)

        self._glow_texture = Texture.create_target(width, height)
        self._glow_texture.set_blend_mode(BlendMode.ADD)

        self._intermediate_texture = Texture.create_target(width, height)
        self._intermediate_texture.set_blend_mode(BlendMode.ADD)

        self._draw_light_texture(self._light_texture, width, height)
        self._draw_light_texture(self._glow_texture, width, height)

    def _draw_light_texture(self, texture: Texture, width: int, height: int) -> None:
        with Renderer.render_target(texture):
            # Clear the texture to black
            Renderer.clear(Color.black())

            # Draw the circle
            center = Point(self.radius, self.radius)
            for y in range(height):
                for x in range(width):
                    p = Point(x, y)
                    d = p.distance_to(center)
                    if d < self.radius:
                        # Apply a linear falloff to the intensity to calculate the color
                        intensity = 1 - (d / self.radius)
                        intensity = int(intensity * 255)
                        color = Color(intensity, intensity, intensity)
                        Renderer.draw_point(p, color)
                    else:
                        Renderer.draw_point(p, Color.black())

    # noinspection DuplicatedCode
    def draw(self, camera: Camera, position: Point, shadow_casters: list[Line] | None = None) -> None:
        """ Draw the light, targeting the camera's lighting pass.

        If shadows are enabled:
            1. The light is drawn to an intermediate texture.
            2. Shadow masks are drawn to the intermediate texture, to mask out portions of the light.
            3. The intermediate texture is drawn to the camera's lighting pass.
        """
        # Calculate the destination rect
        render_position = camera.world_to_render_position(position)
        destination = Rect(
            render_position.x - self.radius,
            render_position.y - self.radius,
            self._light_texture.width,
            self._light_texture.height
        )

        if self.cast_shadows and shadow_casters:
            # Draw the light to the intermediate texture
            texture = self._intermediate_texture
            with Renderer.render_target(texture):
                Renderer.clear(Color.black())
                Renderer.copy(
                    texture=self._light_texture,
                    source_rect=None,
                    destination_rect=None,
                    rotation_angle=0,
                    rotation_center=None,
                    flip=0
                )

                # Draw shadows on top of the light texture
                for line in shadow_casters:
                    self._draw_shadow_mask(position, line)
        else:
            texture = self._light_texture

        if self.intensity:
            with camera.render_pass("Lighting"):
                Renderer.set_texture_color_mod(texture, self.color)
                Renderer.set_texture_alpha_mod(texture, int(self._intensity * 255))

                Renderer.copy(
                    texture=texture,
                    source_rect=None,
                    destination_rect=destination,
                    rotation_angle=0,
                    rotation_center=None,
                    flip=0
                )

                Renderer.clear_texture_color_mod(texture)
                Renderer.clear_texture_alpha_mod(texture)

        if self.glow_intensity:
            with camera.render_pass("Glow"):
                Renderer.set_texture_color_mod(texture, self.color)
                Renderer.set_texture_alpha_mod(texture, int(self._glow_intensity * 255))

                Renderer.copy(
                    texture=texture,
                    source_rect=None,
                    destination_rect=destination,
                    rotation_angle=0,
                    rotation_center=None,
                    flip=0
                )

                Renderer.clear_texture_color_mod(texture)
                Renderer.clear_texture_alpha_mod(texture)

    def _draw_shadow_mask(self, light_position: Point, line: Line) -> None:
        """ Project a line segment away from the light's origin to generate a shadow mask.
        https://slembcke.github.io/SuperFastHardShadows
        The '999' magic number is just a constant to make sure the end distance of the shadow mask is sufficiently far
            away from the light so that the mask extends past the radius.
        """
        v0 = line.a - light_position + self._center_offset
        v1 = line.a + ((line.a - light_position) * 999) - light_position + self._center_offset
        v2 = line.b - light_position + self._center_offset
        v3 = line.b + ((line.b - light_position) * 999) - light_position + self._center_offset
        Renderer.render_geometry([v0, v1, v2, v1, v2, v3], Color.black())
