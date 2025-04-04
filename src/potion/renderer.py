from __future__ import annotations

from contextlib import contextmanager
from ctypes import byref, c_int, pointer, POINTER
from pathlib import Path
from typing import Callable, Generator, TYPE_CHECKING

import sdl2
import sdl2.sdlimage
from sdl2 import sdlgfx

from potion.callback_list import CallbackList
from potion.data_types.blend_mode import BlendMode
from potion.data_types.color import Color

if TYPE_CHECKING:
    from potion.content_types.texture import Texture
    from potion.data_types.circle import Circle
    from potion.data_types.line import Line
    from potion.data_types.point import Point
    from potion.data_types.rect import Rect


class Renderer:
    """ The rendering context for the window. """
    _initialized = False

    _resolution = (0, 0)
    _sdl_renderer = None

    _clip_rect: Rect | None = None

    _reset_callbacks = CallbackList("RendererReset")
    _resolution_change_callbacks = CallbackList("RendererResolutionChange")

    @classmethod
    def init(cls, resolution: tuple[int, int], flags: int = 0) -> None:
        """ Initialize the renderer. """
        from potion.window import Window

        if cls._initialized:
            raise RuntimeError("The renderer has already been initialized.")

        if not Window._initialized:  # noqa
            raise RuntimeError("The window must be initialized before the renderer.")

        cls._resolution = resolution

        # Create SDL renderer
        cls._sdl_renderer = sdl2.SDL_CreateRenderer(Window.sdl_window(), -1, flags)

        cls._initialized = True

    @classmethod
    def init_default(cls) -> None:
        """ Initialize the renderer with default settings. """
        resolution = (320, 180)
        flags = 0
        flags |= sdl2.SDL_RENDERER_PRESENTVSYNC
        cls.init(resolution=resolution, flags=flags)

    @classmethod
    def ensure_init(cls) -> None:
        """ Make sure the renderer has been initialized. """
        if not cls._initialized:
            raise RuntimeError("The renderer has not been initialized. Make sure to run `Renderer.init()`.")

    @classmethod
    def resolution(cls) -> tuple[int, int]:
        """ The native resolution that the game renders at.
        The game viewport will be scaled to fit the window relative to the game resolution.
        """
        return cls._resolution

    @classmethod
    def set_resolution(cls, resolution: tuple[int, int]) -> None:
        cls._resolution = resolution
        cls.on_renderer_resolution_change()

    @classmethod
    def enable_vsync(cls) -> None:
        """ Enables VSync. """
        sdl2.SDL_RenderSetVSync(cls._sdl_renderer, 1)

    @classmethod
    def disable_vsync(cls) -> None:
        """ Disables VSync. """
        sdl2.SDL_RenderSetVSync(cls._sdl_renderer, 0)

    @classmethod
    def sdl_renderer(cls) -> POINTER(sdl2.SDL_Renderer):
        """ The SDL Renderer. """
        return cls._sdl_renderer

    @classmethod
    def name(cls) -> str:
        """ The name of the SDL renderer. """
        info = sdl2.SDL_RendererInfo()
        sdl2.SDL_GetRendererInfo(cls._sdl_renderer, info)
        return info.name.decode("utf-8")

    @classmethod
    def set_render_target(cls, texture: Texture) -> None:
        """ Set the render target to a texture. """
        sdl2.SDL_SetRenderTarget(cls._sdl_renderer, texture.sdl_texture)

    @classmethod
    def unset_render_target(cls) -> None:
        """ Clear the current render target; it will be set back to the window. """
        sdl2.SDL_SetRenderTarget(cls._sdl_renderer, None)

    @classmethod
    @contextmanager
    def render_target(cls, texture: Texture) -> Generator:
        """ Context manager to temporarily render to a target texture. """
        old_clip_rect = cls._clip_rect
        old_target = sdl2.SDL_GetRenderTarget(cls._sdl_renderer)
        Renderer.set_render_target(texture)

        yield

        sdl2.SDL_SetRenderTarget(cls._sdl_renderer, old_target)
        cls.set_clip_rect(old_clip_rect)

    @classmethod
    def set_clip_rect(cls, rect: Rect | None) -> None:
        """ Set the clip rectangle for rendering.
        IMPORTANT:Changing the render target with the clip rect active will clear the current clip rect.
        """
        cls._clip_rect = rect
        if rect:
            rect = rect.to_sdl_rect()
        sdl2.SDL_RenderSetClipRect(cls._sdl_renderer, rect)

    @classmethod
    def clear(cls, color: Color = Color.transparent()) -> None:
        """ Clear the current rendering target. """
        sdl2.SDL_SetRenderDrawColor(cls._sdl_renderer, *color)
        sdl2.SDL_RenderClear(cls._sdl_renderer)

    @classmethod
    def copy(cls,
             texture: Texture,
             source_rect: Rect | None,
             destination_rect: Rect | None,
             rotation_angle: float,
             rotation_center: Point | None,
             flip: int,
             ) -> None:
        """ Copy a texture to the rendering target. """
        if source_rect:
            source_rect = source_rect.to_sdl_rect()

        if destination_rect:
            destination_rect = destination_rect.to_sdl_rect()

        if rotation_center:
            rotation_center = pointer(rotation_center.to_sdl_point())

        sdl2.SDL_RenderCopyEx(
            cls._sdl_renderer,
            texture.sdl_texture,
            source_rect,
            destination_rect,
            rotation_angle,
            rotation_center,
            flip
        )

    @classmethod
    def present(cls) -> None:
        """ Update the screen with any rendering performed since the previous call. """
        sdl2.SDL_RenderPresent(cls._sdl_renderer)

    @classmethod
    def draw_point(cls, point: Point, color: Color) -> None:
        """ Draw a point. """
        sdl2.SDL_SetRenderDrawColor(cls._sdl_renderer, *color)
        sdl2.SDL_RenderDrawPoint(cls._sdl_renderer, point.x, point.y)

    @classmethod
    def draw_points(cls, points: list[Point], color: Color) -> None:
        """ Draw a list of points. """
        sdl2.SDL_SetRenderDrawColor(cls._sdl_renderer, *color)
        sdl_points = [p.to_sdl_point() for p in points]
        points_ptr = (sdl2.SDL_Point * len(points))(*sdl_points)
        sdl2.SDL_RenderDrawPoints(cls._sdl_renderer, points_ptr, len(points))

    @classmethod
    def draw_line(cls, line: Line, color: Color) -> None:
        """ Draw a line. """
        sdl2.SDL_SetRenderDrawColor(cls._sdl_renderer, *color)
        sdl2.SDL_RenderDrawLine(cls._sdl_renderer, line.a.x, line.a.y, line.b.x, line.b.y)

    @classmethod
    def draw_thick_line(cls, line: Line, thickness: int, color: Color) -> None:
        """ Draw a line with thickness. """
        sdl2.SDL_SetRenderDrawColor(cls._sdl_renderer, *color)
        sdlgfx.thickLineRGBA(cls._sdl_renderer, line.a.x, line.a.y, line.b.x, line.b.y, thickness, *color)

    @classmethod
    def draw_rect_outline(cls, rect: Rect, color: Color) -> None:
        """ Draw the outline of a rectangle. """
        sdl2.SDL_SetRenderDrawColor(cls._sdl_renderer, *color)
        sdl2.SDL_RenderDrawRect(cls._sdl_renderer, rect.to_sdl_rect())

    @classmethod
    def draw_rect_solid(cls, rect: Rect, color: Color) -> None:
        """ Draw a solid rectangle. """
        sdl2.SDL_SetRenderDrawColor(cls._sdl_renderer, *color)
        sdl2.SDL_RenderFillRect(cls._sdl_renderer, rect.to_sdl_rect())

    @classmethod
    def draw_rounded_rect_outline(cls, rect: Rect, radius: int, color: Color) -> None:
        """ Draw the outline of a rectangle with rounded corners. """
        sdlgfx.roundedRectangleRGBA(cls._sdl_renderer, rect.right(), rect.y, rect.x, rect.bottom(), radius, *color)

    @classmethod
    def draw_rounded_rect_solid(cls, rect: Rect, radius: int, color: Color) -> None:
        """ Draw a solid rectangle with rounded corners. """
        sdlgfx.roundedBoxRGBA(cls._sdl_renderer, rect.right(), rect.y, rect.x, rect.bottom(), radius, *color)

        # Also draw the outline version.
        # For some reason, the roundedBox edges don't match up with the roundedRectangle edges.
        # Drawing both ensures that the outline for both is the same.
        sdlgfx.roundedRectangleRGBA(cls._sdl_renderer, rect.right(), rect.y, rect.x, rect.bottom(), radius, *color)

    @classmethod
    def draw_rect_with_optional_rounded_corners_solid(cls,
                                                      rect: Rect,
                                                      radius: int,
                                                      top_left: bool,
                                                      top_right: bool,
                                                      bottom_left: bool,
                                                      bottom_right: bool,
                                                      color: Color,
                                                      ) -> None:
        """ Draw a solid rectangle.
        Each corner can be rounded (if True) or right-angle (if False).
        """
        # Draw rounded rectangle
        sdlgfx.roundedBoxRGBA(cls._sdl_renderer, rect.right(), rect.y, rect.x, rect.bottom(), radius, *color)
        sdlgfx.roundedRectangleRGBA(cls._sdl_renderer, rect.right(), rect.y, rect.x, rect.bottom(), radius, *color)

        # Draw corners
        sdl2.SDL_SetRenderDrawColor(cls._sdl_renderer, *color)
        if not top_left:
            sdl2.SDL_RenderFillRect(
                cls._sdl_renderer,
                sdl2.SDL_Rect(rect.left(), rect.top(), radius, radius)
            )
        if not top_right:
            sdl2.SDL_RenderFillRect(
                cls._sdl_renderer,
                sdl2.SDL_Rect(rect.right() - radius + 1, rect.top(), radius, radius)
            )
        if not bottom_left:
            sdl2.SDL_RenderFillRect(
                cls._sdl_renderer,
                sdl2.SDL_Rect(rect.left(), rect.bottom() - radius + 1, radius, radius)
            )
        if not bottom_right:
            sdl2.SDL_RenderFillRect(
                cls._sdl_renderer,
                sdl2.SDL_Rect(rect.right() - radius + 1, rect.bottom() - radius + 1, radius, radius)
            )

    @classmethod
    def draw_circle_outline(cls, circle: Circle, color: Color) -> None:
        """ Draw the outline of a circle. """
        sdlgfx.circleRGBA(cls._sdl_renderer, circle.x, circle.y, circle.radius, *color)

    @classmethod
    def draw_circle_solid(cls, circle: Circle, color: Color) -> None:
        """ Draw a solid circle. """
        sdlgfx.filledCircleRGBA(cls._sdl_renderer, circle.x, circle.y, circle.radius, *color)

    @classmethod
    def render_geometry(cls, vertices: list[Point], color: Color) -> None:
        """ Render triangles.

        The list of vertices is interpreted as points on a triangle. Example:

        vertices = [Point(0, 0), Point(0, 100), Point(100, 100), Point(100, 100), Point(100, 0), Point(0, 0)]
                    └────────────────────┬────────────────────┘  └────────────────────┬────────────────────┘
                                     Triangle 1                                   Triangle 2
        """
        sdl_vertices = [sdl2.SDL_Vertex((v.x, v.y), color.to_tuple()) for v in vertices]
        vertices_ptr = (sdl2.SDL_Vertex * len(vertices))(*sdl_vertices)
        sdl2.SDL_RenderGeometry(cls._sdl_renderer, None, vertices_ptr, len(vertices), None, 0)

    @classmethod
    def add_reset_callback(cls, callback: Callable) -> None:
        """ Add a callback to be run when the render targets or device resets. """
        cls._reset_callbacks.append(callback)

    @classmethod
    def remove_reset_callback(cls, callback: Callable) -> None:
        """ Remove a render reset callback. """
        cls._reset_callbacks.remove(callback)

    @classmethod
    def on_renderer_reset(cls) -> None:
        """ Called when the render targets or device has been reset. """
        cls._reset_callbacks.execute_callbacks()

    @classmethod
    def add_resolution_change_callback(cls, callback: Callable) -> None:
        """ Add a callback to be run when the renderer resolution changes sizes. """
        cls._resolution_change_callbacks.append(callback)

    @classmethod
    def remove_resolution_change_callback(cls, callback: Callable) -> None:
        """ Remove a render resolution change callback. """
        cls._resolution_change_callbacks.remove(callback)

    @classmethod
    def on_renderer_resolution_change(cls) -> None:
        """ Called when the renderer's resolution changes. """
        cls._resolution_change_callbacks.execute_callbacks()

    @classmethod
    def set_render_draw_blend_mode(cls, blend_mode: BlendMode) -> None:
        """ Set the blend mode used for drawing operations (Fill and Line). """
        match blend_mode:
            case BlendMode.NONE:
                sdl2.SDL_SetRenderDrawBlendMode(cls._sdl_renderer, sdl2.SDL_BLENDMODE_NONE)
            case BlendMode.BLEND:
                sdl2.SDL_SetRenderDrawBlendMode(cls._sdl_renderer, sdl2.SDL_BLENDMODE_BLEND)
            case BlendMode.ADD:
                sdl2.SDL_SetRenderDrawBlendMode(cls._sdl_renderer, sdl2.SDL_BLENDMODE_ADD)
            case BlendMode.MOD:
                sdl2.SDL_SetRenderDrawBlendMode(cls._sdl_renderer, sdl2.SDL_BLENDMODE_MOD)
            case BlendMode.MUL:
                sdl2.SDL_SetRenderDrawBlendMode(cls._sdl_renderer, sdl2.SDL_BLENDMODE_MUL)

    @classmethod
    def clear_render_draw_blend_mode(cls) -> None:
        """ Clear the render draw blend mode. """
        sdl2.SDL_SetRenderDrawBlendMode(cls._sdl_renderer, sdl2.SDL_BLENDMODE_NONE)

    @classmethod
    def write_png(cls, file: Path) -> None:
        """ Write the image from the current rendering target to a PNG. """
        # Get the width and height of the current render target
        width = c_int()
        height = c_int()
        sdl2.SDL_GetRendererOutputSize(cls._sdl_renderer, byref(width), byref(height))
        width = width.value
        height = height.value

        # Create surface
        surface = sdl2.SDL_CreateRGBSurfaceWithFormat(0, width, height, 32, sdl2.SDL_PIXELFORMAT_ARGB8888)

        # Read pixels
        sdl2.SDL_RenderReadPixels(
            Renderer.sdl_renderer(),
            None,
            sdl2.SDL_PIXELFORMAT_ARGB8888,
            surface.contents.pixels,
            surface.contents.pitch,
        )

        # Write thumbnail
        sdl2.sdlimage.IMG_SavePNG(surface, file.as_posix().encode())

        # Free surface
        sdl2.SDL_FreeSurface(surface)

    @staticmethod
    def set_texture_color_mod(texture: Texture, color: Color) -> None:
        """ Set an additional color value multiplied into render copy operations. """
        sdl2.SDL_SetTextureColorMod(texture.sdl_texture, color.r, color.g, color.b)

    @staticmethod
    def clear_texture_color_mod(texture: Texture) -> None:
        """ Clear the texture's color mod. """
        sdl2.SDL_SetTextureColorMod(texture.sdl_texture, 255, 255, 255)

    @staticmethod
    def set_texture_alpha_mod(texture: Texture, alpha: int) -> None:
        """ Set an additional alpha value multiplied into render copy operations """
        sdl2.SDL_SetTextureAlphaMod(texture.sdl_texture, alpha)

    @staticmethod
    def clear_texture_alpha_mod(texture: Texture) -> None:
        """ Clear the texture alpha mod. """
        sdl2.SDL_SetTextureAlphaMod(texture.sdl_texture, 255)
