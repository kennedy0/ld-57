from __future__ import annotations

from math import floor
from typing import TYPE_CHECKING

import sdl2

from potion.atlas import Atlas
from potion.content import Content
from potion.content_types.texture import Texture
from potion.data_types.blend_mode import BlendMode
from potion.data_types.color import Color
from potion.data_types.pivot import Pivot
from potion.data_types.point import Point
from potion.data_types.rect import Rect
from potion.frame import Frame
from potion.log import Log
from potion.renderer import Renderer
from potion.utilities import pmath

if TYPE_CHECKING:
    from potion.camera import Camera


class Sprite:
    """ A 2D sprite object. """
    def __init__(self, content_path: str) -> None:
        """ `content_path` is the path to the sprite image texture file. """
        self._name = content_path
        self._rotation = 0
        self._scale = 1.0
        self._pivot = Pivot()
        self._flip_horizontal = False
        self._flip_vertical = False
        self._flip = 0
        self._color = None
        self._opacity = 255
        self._flash_texture = Texture.create_target(2, 2)
        self._flash_color = Color.white()
        self._flash_opacity = 0

        if content_path == "empty-sprite":
            self._texture = Texture.create_static(0, 0)
        else:
            self._texture = Content.load_texture(content_path)

        # Set the source rect for drawing
        self._source_rect: Rect = Rect(0, 0, self._texture.width, self._texture.height)

        # Store the unscaled size of the original texture
        # The real width and height of the sprite may change if a scale is applied
        self._unscaled_width = self._texture.width
        self._unscaled_height = self._texture.height

        # Track the atlas that the sprite came from (if any)
        self._atlas: Atlas | None = None

        # Optional frame data for sprites that are loaded from an atlas
        self._frame_offset_top: int = 0
        self._frame_offset_left: int = 0
        self._frame_offset_right: int = 0
        self._frame_offset_bottom: int = 0
        self._frame_offset: Point = Point.zero()

        # Initialize flash texture
        self._reset_flash_texture()

        # Callbacks
        Renderer.add_reset_callback(self._reset_flash_texture)

    def __del__(self) -> None:
        Renderer.remove_reset_callback(self._reset_flash_texture)

    def __str__(self) -> str:
        return f"Sprite({self.name})"

    def __repr__(self) -> str:
        return str(self)

    def __bool__(self) -> bool:
        return not self.is_empty()

    @property
    def name(self) -> str:
        """ The name of the sprite. """
        return self._name

    @property
    def texture(self) -> Texture:
        """ The texture that the sprite draws. """
        return self._texture
    
    @property
    def scale(self) -> float:
        """ The scale of the sprite. """
        return self._scale
    
    @scale.setter
    def scale(self, value: float) -> None:
        self._scale = value
    
    @property
    def rotation(self) -> int:
        """ The angle (in degrees) to rotate the sprite clockwise. """
        return self._rotation
    
    @rotation.setter
    def rotation(self, value: int) -> None:
        self._rotation = int(value)

    @property
    def pivot(self) -> Pivot:
        """ The pivot point of the sprite. """
        return self._pivot

    @property
    def flip_horizontal(self) -> bool:
        """ If true, the sprite is flipped horizontally. """
        return self._flip_horizontal

    @flip_horizontal.setter
    def flip_horizontal(self, value: bool) -> None:
        self._flip_horizontal = value

        self._flip = 0
        if self._flip_horizontal:
            self._flip |= sdl2.SDL_FLIP_HORIZONTAL
        if self._flip_vertical:
            self._flip |= sdl2.SDL_FLIP_VERTICAL

    @property
    def flip_vertical(self) -> bool:
        """ If true, the sprite is flipped vertically. """
        return self._flip_vertical

    @flip_vertical.setter
    def flip_vertical(self, value: bool) -> None:
        self._flip_vertical = value

        self._flip = 0
        if self._flip_horizontal:
            self._flip |= sdl2.SDL_FLIP_HORIZONTAL
        if self._flip_vertical:
            self._flip |= sdl2.SDL_FLIP_VERTICAL

    @property
    def color(self) -> Color | None:
        """ Adds a color tint to the sprite.
        This only sets RGB values; alpha channel does nothing.
        """
        return self._color

    @color.setter
    def color(self, value: Color | None) -> None:
        """ Setting the tint to 'None' removes the tint. """
        self._color = value

    @property
    def opacity(self) -> int:
        """ The opacity of the sprite. """
        return self._opacity

    @opacity.setter
    def opacity(self, value: int) -> None:
        """ Opacity can be set as a 0-255 int value. """
        self._opacity = pmath.clamp(value, 0, 255)

    @property
    def flash_color(self) -> Color:
        """ Adds a color overlay to the sprite.
        This only sets RGB values; alpha channel does nothing.
        """
        return self._flash_color

    @flash_color.setter
    def flash_color(self, value: Color) -> None:
        self._flash_color = value

    @property
    def flash_opacity(self) -> int:
        """ The opacity of the color overlay. """
        return self._flash_opacity

    @flash_opacity.setter
    def flash_opacity(self, value: int) -> None:
        """ Opacity can be set as a 0-255 int value.
        Setting the opacity to 0 removes the flash.
        """
        self._flash_opacity = pmath.clamp(value, 0, 255)

    @classmethod
    def from_atlas(cls, content_path: str, sprite_name: str) -> Sprite:
        """ Factory method to create a sprite from an atlas.
        `content_path` is the path to the sprite atlas texture file.
        `sprite_name` can be either a frame name ("MySprite.0001") or the sprite's original filename ("MySprite").
        """
        # Create sprite
        sprite = cls(content_path)
        sprite._name = sprite_name

        # Create atlas
        atlas = Atlas.instance(content_path)

        # Get frame data from atlas
        if sprite_name in atlas.frame_names:
            frame = atlas.frame(sprite_name)
        elif sprite_name in atlas.sprites:
            frame = atlas.animation_frames(sprite_name, "default")[0]
        else:
            Log.error(f"Could not find frame or sprite named '{sprite_name}' in {atlas}")
            return sprite.empty()

        # Apply frame data to sprite
        sprite._atlas = atlas
        sprite._apply_frame_data(frame)

        return sprite

    @classmethod
    def from_frame(cls, content_path: str, frame: Frame) -> Sprite:
        """ Factory method to create a sprite from a frame.
        `content_path` is the path to the sprite image texture file.
        """
        sprite = Sprite(content_path)
        sprite._apply_frame_data(frame)
        return sprite

    @classmethod
    def empty(cls) -> Sprite:
        """ Create an empty sprite with no texture. """
        return cls("empty-sprite")

    def is_empty(self) -> bool:
        """ Check if this is an empty sprite with no texture. """
        return self.name == "empty-sprite"

    def width(self) -> int:
        """ The width of the sprite. """
        return floor(self._unscaled_width * self.scale)

    def height(self) -> int:
        """ The height of the sprite. """
        return floor(self._unscaled_height * self.scale)

    def pivot_offset(self) -> Point:
        """ Get the offset for the pivot point. """
        return Point(self._pivot.x * self.width(), self._pivot.y * self.height())

    def frame_offset(self) -> Point:
        """ Get the frame offset.

        This is to account for transparent edge trimming when sprites are packed into an atlas, and their frame sizes
        don't match the original sprite sizes.

        Therefore, it's necessary to apply an additional offset to compensate for the distance that the sprite should
        be from the top-left corner.

        Additionally, we have to consider if the sprite is flipped horizontal or vertical, since the offset amount may
        be different.

        This offset will always be zero if the sprite wasn't loaded from frame data.
        """
        if self.flip_horizontal:
            x = self._frame_offset_right * self._scale
        else:
            x = self._frame_offset_left * self._scale

        if self.flip_vertical:
            y = self._frame_offset_bottom * self._scale
        else:
            y = self._frame_offset_top * self._scale

        return Point(x, y)

    def set_texture_blend_mode(self, blend_mode: BlendMode) -> None:
        """ Set the sprite's texture's blend mode. """
        if self._atlas:
            Log.error(f"{self} belongs to {self._atlas}; must set the blend mode on the atlas directly")
            return
        self._texture.set_blend_mode(blend_mode)

    def draw(self, camera: Camera, position: Point) -> None:
        """ Draw the sprite at a given position. """
        # Convert world position to render position
        render_position = camera.world_to_render_position(position)

        # Get draw position by applying offsets to the render position
        draw_position = render_position - self.pivot_offset() + self.frame_offset()

        # Set destination rect
        destination_w = floor(self._source_rect.width * self._scale)
        destination_h = floor(self._source_rect.height * self._scale)
        destination = Rect(draw_position.x, draw_position.y, destination_w, destination_h)

        # If there is rotation, calculate the center point
        rotation_center = None
        if self._rotation:
            rotation_center = self.pivot_offset() - self.frame_offset()

        # Apply tint
        if self.color:
            Renderer.set_texture_color_mod(self._texture, self.color)

        # Apply opacity
        if self.opacity != 255:
            Renderer.set_texture_alpha_mod(self._texture, self.opacity)

        # Render texture
        Renderer.copy(
            texture=self._texture,
            source_rect=self._source_rect,
            destination_rect=destination,
            rotation_angle=self._rotation,
            rotation_center=rotation_center,
            flip=self._flip
        )

        # Clear tint
        if self.color:
            Renderer.clear_texture_color_mod(self._texture)

        # Clear opacity
        if self.opacity != 255:
            Renderer.clear_texture_alpha_mod(self._texture)

        # Flash
        if not self._flash_opacity:
            return

        # Create mask
        # 1. Clear the flash texture
        # 2. Draw the sprite to the flash texture
        # 3. Add white over the texture - this creates a full white mask
        with Renderer.render_target(self._flash_texture):
            Renderer.clear()
            Renderer.copy(
                texture=self._texture,
                source_rect=self._source_rect,
                destination_rect=None,
                rotation_angle=0,
                rotation_center=None,
                flip=0,
            )
            Renderer.set_render_draw_blend_mode(BlendMode.ADD)
            Renderer.draw_rect_solid(Rect(0, 0, self._source_rect.width, self._source_rect.height), Color.white())
            Renderer.clear_render_draw_blend_mode()

        # Set color and opacity
        Renderer.set_texture_color_mod(self._flash_texture, self._flash_color)
        Renderer.set_texture_alpha_mod(self._flash_texture, self._flash_opacity)

        # Render flash texture
        Renderer.copy(
            texture=self._flash_texture,
            source_rect=None,
            destination_rect=destination,
            rotation_angle=self.rotation,
            rotation_center=rotation_center,
            flip=self._flip
        )

    def _apply_frame_data(self, frame: Frame):
        """ Read frame data from an atlas and apply it to the sprite. """
        # Set source rect
        self._source_rect = Rect(frame.x, frame.y, frame.frame_width, frame.frame_height)

        # Set unscaled width and height
        self._unscaled_width = frame.sprite_width
        self._unscaled_height = frame.sprite_height

        # Set frame offset
        self._frame_offset_top = frame.offset_y
        self._frame_offset_left = frame.offset_x
        self._frame_offset_right = frame.sprite_width - frame.frame_width - frame.offset_x
        self._frame_offset_bottom = frame.sprite_height - frame.frame_height - frame.offset_y

        # Reset the flash texture
        self._reset_flash_texture()

    def _reset_flash_texture(self) -> None:
        """ Create the flash texture. """
        self._flash_texture = Texture.create_target(self._source_rect.width, self._source_rect.height)
        self._flash_texture.set_blend_mode(BlendMode.BLEND)
