from __future__ import annotations

from contextlib import contextmanager
from enum import Enum
from math import floor
from typing import Generator, TYPE_CHECKING

from potion.content_types.texture import Texture
from potion.data_types.blend_mode import BlendMode
from potion.data_types.color import Color
from potion.data_types.point import Point
from potion.data_types.rect import Rect
from potion.data_types.scale_mode import ScaleMode
from potion.data_types.vector2 import Vector2
from potion.engine import Engine
from potion.entity_list import EntityList
from potion.log import Log
from potion.renderer import Renderer
from potion.render_pass import RenderPass
from potion.utilities import pmath
from potion.window import Window

if TYPE_CHECKING:
    from potion.entity import Entity
    from potion.scene import Scene


class ResizeMode(Enum):
    NONE = 0
    WIDTH = 1
    HEIGHT = 2
    FIT = 3
    FILL = 4
    DISTORT = 5


class Camera:
    """ A camera renders entities to the screen.

    A high-level overview of the camera rendering process is:
        1. For all valid entities, draw to the render passes textures
        2. Copy all render passes to the camera's render texture
        3. Scale the render texture to match the viewport size
        4. Copy the scaled render texture to the viewport

    The camera renders an extra pixel of width and height so that the scaled render texture can be drawn at sub-pixel
    increments when the camera is moving. This allows for smooth camera movement.
    """
    def __init__(self, name: str, draw_order: int) -> None:
        self._scene = None
        self._name = name
        self._draw_order = draw_order
        self._active = True

        self._resize_mode = ResizeMode.FIT
        self._pixel_perfect_scaling = True
        self._scale_x = 1
        self._scale_y = 1

        self._x = 0.0
        self._y = 0.0

        self._tint = None

        self._include_tags = set()
        self._exclude_tags = set()
        self._include_tags_filter_set = False
        self._exclude_tags_filter_set = False

        # Resolution defaults to game resolution
        self._resolution = Renderer.resolution()

        # Render passes
        self._default_render_pass = RenderPass("Default")
        self._debug_render_pass = RenderPass("Debug")
        self._render_pass_map: dict[str, RenderPass] = {
            'Default': self._default_render_pass,
            'Debug': self._debug_render_pass,
        }
        self._extra_render_passes: list[RenderPass] = []

        # Create a null texture to draw to when an invalid render pass is drawn to
        self._null_texture = Texture.create_target(2, 2)

        # When the camera renders, it draws everything to its render texture.
        # After it is finished drawing, the render texture is scaled and copied to the main window.
        self._render_texture = Texture.create_target(2, 2)

        self._scaled_render_texture = Texture.create_target(2, 2)
        self._scaled_resolution = Renderer.resolution()
        self._offset_x = 0
        self._offset_y = 0

        self._sub_pixel_offset_x = 0
        self._sub_pixel_offset_y = 0

        # Initialize render passes
        self._reset_render_targets()

        # Callbacks
        Window.add_viewport_changed_callback(self._reset_render_targets)
        Renderer.add_reset_callback(self._reset_render_targets)
        Renderer.add_resolution_change_callback(self._reset_render_targets)

    def __del__(self) -> None:
        Window.remove_viewport_changed_callback(self._reset_render_targets)
        Renderer.remove_reset_callback(self._reset_render_targets)
        Renderer.remove_resolution_change_callback(self._reset_render_targets)

    def __str__(self) -> str:
        return f"Camera({self.name})"

    def __repr__(self) -> str:
        return str(self)

    @property
    def scene(self) -> Scene | None:
        """ The scene that the camera belongs to. """
        return self._scene

    @property
    def name(self) -> str:
        """ The name of the camera. """
        return self._name

    @property
    def active(self) -> bool:
        """ If True, the camera is enabled for rendering. """
        return self._active

    @active.setter
    def active(self, value: bool) -> None:
        self._active = value

    @property
    def resize_mode(self) -> ResizeMode:
        """ The mode used when calculating the size of the scaled render texture. """
        return self._resize_mode

    @property
    def pixel_perfect_scaling(self) -> bool:
        """ If True, the render texture will be scaled in pixel-perfect increments when scaling to fit the viewport. """
        return self._pixel_perfect_scaling

    @pixel_perfect_scaling.setter
    def pixel_perfect_scaling(self, value: bool) -> None:
        if value == self._pixel_perfect_scaling:
            return

        self._pixel_perfect_scaling = value
        self._reset_render_targets()

    @property
    def x(self) -> float:
        """ The X position of the camera. """
        return self._x

    @x.setter
    def x(self, value: float) -> None:
        self._x = value

    @property
    def y(self) -> float:
        """ The Y position of the camera. """
        return self._y

    @y.setter
    def y(self, value: float) -> None:
        self._y = value

    @property
    def resolution(self) -> tuple[int, int]:
        """ The resolution that the camera renders at. """
        return self._resolution

    @resolution.setter
    def resolution(self, value: tuple[int, int]) -> None:
        """ Setting the resolution also updates the render texture. """
        if value[0] < 1 or value[1] < 1:
            Log.error(f"Camera resolution must be at least (1, 1); tried to set {value}")
            return

        self._resolution = value
        self._reset_render_targets()

    @property
    def color(self) -> Color | None:
        """ Adds a tint to the camera.
        This only sets RGB values; alpha channel does nothing.
        """
        return self._tint

    @color.setter
    def color(self, value: Color | None) -> None:
        """ Setting the color to 'None' removes the tint. """
        self._tint = value

    @property
    def draw_order(self) -> int:
        """ The draw order of the camera.
        Higher (positive) numbers are drawn in the background; lower (negative) numbers are drawn in the foreground.
        """
        return self._draw_order

    @draw_order.setter
    def draw_order(self, value: int) -> None:
        if self.scene:
            for existing_camera in self.scene.cameras:
                if existing_camera.draw_order == value:
                    Log.error(f"Cannot set {self} draw order to {value};  it would clash with {existing_camera}")
                    return
                self.scene.cameras.flag_list_needs_sorting()
        self._draw_order = value

    def position(self) -> Vector2:
        """ The position of the camera. """
        return Vector2(self._x, self._y)

    def set_position(self, position: Point | Vector2) -> None:
        """ Set the position of the camera. """
        self.x = position.x
        self.y = position.y

    def center(self) -> Vector2:
        """ The position of the center point of the camera. """
        return Vector2(self._x + self._resolution[0] / 2, self._y + self._resolution[1] / 2)

    def rect(self) -> Rect:
        """ The viewport rect of the camera in world space. """
        return Rect(floor(self._x), floor(self._y), self.resolution[0], self.resolution[1])

    def set_resize_mode_none(self) -> None:
        """ The render texture is not resized. """
        self._resize_mode = ResizeMode.NONE
        self._reset_render_targets()

    def set_resize_mode_width(self) -> None:
        """ The render texture is scaled until the width matches the viewport width.
        Height is scaled to preserve the original aspect ratio.
        """
        self._resize_mode = ResizeMode.WIDTH
        self._reset_render_targets()

    def set_resize_mode_height(self) -> None:
        """ The render texture is scaled until the height matches the viewport height.
        Width is scaled to preserve the original aspect ratio.
        """
        self._resize_mode = ResizeMode.HEIGHT
        self._reset_render_targets()

    def set_resize_mode_fit(self) -> None:
        """ The render texture is scaled so that the smallest side fills the viewport's width or height.
        The longest side is scaled to preserve the original aspect ratio
        """
        self._resize_mode = ResizeMode.FIT
        self._reset_render_targets()

    def set_resize_mode_fill(self) -> None:
        """ The render texture is scaled so that the longest side fills the viewport's width or height.
        The smallest side is scaled to preserve the original aspect ratio
        """
        self._resize_mode = ResizeMode.FILL
        self._reset_render_targets()

    def set_resize_mode_distort(self) -> None:
        """ The render texture is scaled to fit the viewport's size.
        This does not preserve the original aspect ratio, so distortion may occur.
        """
        self._resize_mode = ResizeMode.DISTORT
        self._reset_render_targets()

    def include_tag(self, tag: str) -> None:
        """ When set, the camera will only render entities with the include tag(s).
        By default, there are no include tags set, so the camera will render everything.
        """
        self._include_tags.add(tag)
        self._include_tags_filter_set = True

    def clear_include_tags(self) -> None:
        """ Clear the include tags list. """
        self._include_tags.clear()
        self._include_tags_filter_set = False

    def exclude_tag(self, tag: str) -> None:
        """ The camera will never render entities with the exclude tag(s).
        When an entity has tags that match both the include and exclude tags, the exclude tags will take precedence,
        and the entity will not be rendered.
        """
        self._exclude_tags.add(tag)
        self._exclude_tags_filter_set = True

    def clear_exclude_tags(self) -> None:
        """ Clear the exclude tags list. """
        self._exclude_tags.clear()
        self._exclude_tags_filter_set = False

    def get_render_pass(self, name: str) -> RenderPass | None:
        """ Get a render pass. """
        render_pass = self._render_pass_map.get(name)

        if not render_pass:
            Log.error(f"{self} has no render pass named {name}")

        return render_pass

    def add_render_pass(self, render_pass: RenderPass) -> None:
        """ Add a render pass. """
        if render_pass.name in self._render_pass_map:
            Log.error(f"{self} already has a render pass named {render_pass.name}")
            return

        self._extra_render_passes.append(render_pass)
        self._render_pass_map[render_pass.name] = render_pass

    def add_lighting_pass(self) -> None:
        """ Add a lighting render pass. """
        render_pass = RenderPass("Lighting")
        render_pass.set_clear_color(Color.black())
        render_pass.set_blend_mode(BlendMode.MOD)
        self.add_render_pass(render_pass)

    def add_glow_pass(self) -> None:
        """ Add a glow render pass. """
        render_pass = RenderPass("Glow")
        render_pass.set_clear_color(Color.black())
        render_pass.set_blend_mode(BlendMode.ADD)
        self.add_render_pass(render_pass)

    def start(self) -> None:
        """ This runs just before the first update. """
        self._reset_render_targets()

    def draw(self, entities: EntityList) -> None:
        """ Draw entities. """
        self._clear_render_targets()
        self._draw_entities(entities)

        if __debug__:
            if Engine.debug_mode():
                self._debug_draw_entities(entities)

        self._copy_render_passes()
        self._scale_render_texture()
        self._copy_render_texture_to_viewport()

    def _reset_render_targets(self) -> None:
        """ Create the camera's render target textures. """
        # Calculate the scaling needed
        sx = Window.viewport().width / self.resolution[0]
        sy = Window.viewport().height / self.resolution[1]

        match self.resize_mode:
            case ResizeMode.NONE:
                scale_x = 1
                scale_y = 1
            case ResizeMode.WIDTH:
                scale_x = sx
                scale_y = sx
            case ResizeMode.HEIGHT:
                scale_x = sy
                scale_y = sy
            case ResizeMode.FIT:
                scale_x = min(sx, sy)
                scale_y = min(sx, sy)
            case ResizeMode.FILL:
                scale_x = max(sx, sy)
                scale_y = max(sx, sy)
            case ResizeMode.DISTORT:
                scale_x = sx
                scale_y = sy
            case _:
                Log.error(f"Invalid ResizeMode: {self.resize_mode}")
                scale_x = 1
                scale_y = 1

        # Pixel-perfect scale can never be less than one
        if self._pixel_perfect_scaling:
            scale_x = floor(scale_x)
            scale_y = floor(scale_y)
            if scale_x < 1:
                scale_x = 1
            if scale_y < 1:
                scale_y = 1

        # Set the scale and scaled resolution
        self._scale_x = scale_x
        self._scale_y = scale_y
        self._scaled_resolution = (
            int(self._resolution[0] * self._scale_x),
            int(self._resolution[1] * self._scale_y)
        )

        # Calculate the scaled render texture's offset (so it draws in the center)
        self._offset_x = floor((Window.viewport().width - self._scaled_resolution[0]) / 2)
        self._offset_y = floor((Window.viewport().height - self._scaled_resolution[1]) / 2)

        # Calculate the resolution for the render targets
        if (self._scale_x > 1 or self._scale_y) and self._pixel_perfect_scaling:
            # If we're doing pixel-perfect upscaling, add padding so that sub-pixel offsets can be drawn
            w = self.resolution[0] + 1
            h = self.resolution[1] + 1
        else:
            w = self.resolution[0]
            h = self.resolution[1]

        scaled_w = int(w * self._scale_x)
        scaled_h = int(h * self._scale_y)

        # Create the camera's render texture and upscaled render texture
        self._render_texture = Texture.create_target(w, h)
        self._scaled_render_texture = Texture.create_target(scaled_w, scaled_h)
        if self.pixel_perfect_scaling:
            self._render_texture.set_scale_mode(ScaleMode.NEAREST)
            self._scaled_render_texture.set_scale_mode(ScaleMode.NEAREST)
        else:
            self._render_texture.set_scale_mode(ScaleMode.BEST)
            self._scaled_render_texture.set_scale_mode(ScaleMode.BEST)

        self._render_texture.set_blend_mode(BlendMode.ALPHA_COMPOSITE)
        self._scaled_render_texture.set_blend_mode(BlendMode.ALPHA_COMPOSITE)

        # Create a texture for each render pass
        self._default_render_pass.create_texture(w, h)
        self._debug_render_pass.create_texture(w, h)
        for render_pass in self._extra_render_passes:
            render_pass.create_texture(w, h)
            if self.pixel_perfect_scaling:
                render_pass.texture.set_scale_mode(ScaleMode.NEAREST)
            else:
                render_pass.texture.set_scale_mode(ScaleMode.BEST)

        # The null texture is never displayed, so it has a small size
        self._null_texture = Texture.create_target(2, 2)

    def _clear_render_targets(self) -> None:
        """ Clear the camera's render target textures. """
        Renderer.set_render_target(self._render_texture)
        Renderer.clear()

        Renderer.set_render_target(self._scaled_render_texture)
        Renderer.clear()

        self._default_render_pass.clear()
        self._debug_render_pass.clear()
        for render_pass in self._extra_render_passes:
            render_pass.clear()

    def _draw_entities(self, entities: EntityList) -> None:
        """ Draw entities to the camera's render texture.
        The default render pass will be used, unless an entity overrides it in the 'draw()' method.
        """
        with self.render_pass("Default"):
            entities.draw(self)

    def _debug_draw_entities(self, entities: EntityList) -> None:
        """ Draw the debug pass. """
        with self.render_pass("Debug"):
            entities.debug_draw(self)

    def _copy_render_passes(self) -> None:
        """ Copy render passes to the camera's render texture. """
        Renderer.set_render_target(self._render_texture)

        # Default
        Renderer.copy(
            texture=self._default_render_pass.texture,
            source_rect=None,
            destination_rect=None,
            rotation_angle=0,
            rotation_center=None,
            flip=0
        )

        # Extra passes
        for render_pass in self._extra_render_passes:
            Renderer.copy(
                texture=render_pass.texture,
                source_rect=None,
                destination_rect=None,
                rotation_angle=0,
                rotation_center=None,
                flip=0
            )

        # Debug
        if __debug__:
            Renderer.copy(
                texture=self._debug_render_pass.texture,
                source_rect=None,
                destination_rect=None,
                rotation_angle=0,
                rotation_center=None,
                flip=0
            )

        Renderer.unset_render_target()

    def _scale_render_texture(self) -> None:
        """ Scale the render texture to a size matching the viewport. """
        Renderer.set_render_target(self._scaled_render_texture)
        Renderer.copy(
            texture=self._render_texture,
            source_rect=None,
            destination_rect=None,
            rotation_angle=0,
            rotation_center=None,
            flip=0
        )

    def _copy_render_texture_to_viewport(self) -> None:
        """ Copy the camera's render texture to the window's viewport texture. """
        Renderer.set_render_target(Window.viewport_texture())

        # Apply tint
        if self.color:
            Renderer.set_texture_color_mod(self._scaled_render_texture, self.color)

        # Calculate the source and destination rects
        # If doing pixel-perfect upscaling, calculate sub-pixel offsets for smooth drawing
        if (self._scale_x > 1 or self._scale_y > 1) and self._pixel_perfect_scaling:
            xr = self.x % 1
            yr = self.y % 1
            self._sub_pixel_offset_x = floor(xr * self._scale_x)
            self._sub_pixel_offset_y = floor(yr * self._scale_y)
        else:
            self._sub_pixel_offset_x = 0
            self._sub_pixel_offset_x = 0

        source = Rect(
            self._sub_pixel_offset_x,
            self._sub_pixel_offset_y,
            self._scaled_resolution[0],
            self._scaled_resolution[1]
        )
        destination = Rect(
            self._offset_x,
            self._offset_y,
            self._scaled_resolution[0],
            self._scaled_resolution[1]
        )

        # Copy render texture
        Renderer.copy(
            texture=self._scaled_render_texture,
            source_rect=source,
            destination_rect=destination,
            rotation_angle=0,
            rotation_center=None,
            flip=0
        )

        # Clear tint
        if self.color:
            Renderer.clear_texture_color_mod(self._scaled_render_texture)

        Renderer.unset_render_target()

    def world_to_render_position(self, world_position: Point) -> Point:
        """ Convert a world position to a position relative to the camera's render texture. """
        return world_position - self.position().to_point()

    def render_to_world_position(self, camera_position: Point) -> Point:
        """ Convert a position relative to the camera's render texture to a world position. """
        return camera_position + self.position().to_point()

    def screen_to_world_position(self, screen_position: Point) -> Point:
        """ Convert a screen position to a world position. """
        render_position = self.screen_to_render_position(screen_position)
        return self.render_to_world_position(render_position)

    def screen_to_render_position(self, screen_position: Point) -> Point:
        """ Convert a screen position to a position relative to the camera's render texture. """
        resolution_x, resolution_y = self.resolution
        viewport = Window.viewport()
        screen_x = screen_position.x + self._sub_pixel_offset_x
        screen_y = screen_position.y + self._sub_pixel_offset_y
        x = pmath.remap(screen_x, viewport.left(), viewport.right(), 0, resolution_x)
        y = pmath.remap(screen_y, viewport.top(), viewport.bottom(), 0, resolution_y)
        return Point(x, y)

    def can_draw_entity(self, entity: Entity) -> bool:
        """ Check if an entity can be drawn by the camera. """
        # If no tag filters have been set, the entity will always be visible
        if not self._include_tags_filter_set and not self._exclude_tags_filter_set:
            return True

        # Filter out excluded entities
        if self._exclude_tags_filter_set:
            if not self._exclude_tags.isdisjoint(entity.tags):
                return False

        # Filter out non-matching included entities
        if self._include_tags_filter_set:
            if self._include_tags.isdisjoint(entity.tags):
                return False

        return True

    @contextmanager
    def render_pass(self, name: str) -> Generator:
        """ Context manager to render to a specific render pass. """
        render_pass = self._render_pass_map.get(name)

        if render_pass:
            target = render_pass.texture
        else:
            Log.error(f"{self} has no render pass named {name}")
            target = self._null_texture

        with Renderer.render_target(target):
            yield
