from __future__ import annotations

from ctypes import byref, c_int, POINTER
from io import BytesIO
from pathlib import Path

import sdl2
import sdl2.sdlimage

from potion.data_types.blend_mode import BlendMode
from potion.data_types.scale_mode import ScaleMode


POTION_BLENDMODE_ALPHA_COMPOSITE = sdl2.SDL_ComposeCustomBlendMode(
    sdl2.SDL_BLENDFACTOR_ONE,
    sdl2.SDL_BLENDFACTOR_ONE_MINUS_SRC_ALPHA,
    sdl2.SDL_BLENDOPERATION_ADD,
    sdl2.SDL_BLENDFACTOR_ONE,
    sdl2.SDL_BLENDFACTOR_ONE_MINUS_SRC_ALPHA,
    sdl2.SDL_BLENDOPERATION_ADD,
)


class Texture:
    """ A wrapper around SDL_Texture.

    New instances of this shouldn't be created manually, instead the factory methods should be used to more easily
    initialize the texture.
    """
    def __init__(self,
                 width: int,
                 height: int,
                 sdl_texture: POINTER(sdl2.SDL_Texture) | None,
                 name: str | None = None
                 ) -> None:
        self._width = width
        self._height = height
        self._sdl_texture = sdl_texture
        self._name = name
        self._scale_mode = ScaleMode.NEAREST
        self._blend_mode = BlendMode.NONE

    def __del__(self):
        sdl2.SDL_DestroyTexture(self.sdl_texture)

    def __str__(self) -> str:
        if self._name:
            return f"Texture(name={self._name}, width={self.width}, height={self.height})"
        else:
            return f"Texture(width={self.width}, height={self.height})"

    def __repr__(self) -> str:
        return str(self)

    @property
    def width(self) -> int:
        """ The width of the texture. """
        return self._width

    @property
    def height(self) -> int:
        """ The height of the texture. """
        return self._height

    @property
    def sdl_texture(self) -> POINTER(sdl2.SDL_Texture):
        """ Pointer to the SDL texture. """
        return self._sdl_texture

    @property
    def name(self) -> str | None:
        """ The name of the texture. """
        return self._name

    @property
    def scale_mode(self) -> ScaleMode:
        """ The scale mode used in drawing operations. """
        return self._scale_mode

    @property
    def blend_mode(self) -> BlendMode:
        """ The blend mode used in drawing operations. """
        return self._blend_mode

    @staticmethod
    def _create_new(width: int, height: int, access: int) -> Texture:
        """ Create a new texture. """
        from potion.renderer import Renderer

        pixel_format = sdl2.SDL_PIXELFORMAT_RGBA8888
        sdl_texture = sdl2.SDL_CreateTexture(Renderer.sdl_renderer(), pixel_format, access, width, height)
        return Texture(width, height, sdl_texture)

    @staticmethod
    def create_static(width: int, height: int) -> Texture:
        """ Create a static texture that can't be changed. """
        return Texture._create_new(width, height, sdl2.SDL_TEXTUREACCESS_STATIC)

    @staticmethod
    def create_streaming(width: int, height: int) -> Texture:
        """ Create a texture that can have its pixel data changed. """
        return Texture._create_new(width, height, sdl2.SDL_TEXTUREACCESS_STREAMING)

    @staticmethod
    def create_target(width: int, height: int) -> Texture:
        """ Create a texture that can be used as a render target. """
        return Texture._create_new(width, height, sdl2.SDL_TEXTUREACCESS_TARGET)

    @staticmethod
    def from_file(image_file: Path) -> Texture:
        """ Create a texture from an image file. """
        from potion.renderer import Renderer

        # Load SDL texture
        with image_file.open('rb') as fp:
            rw = sdl2.rw_from_object(BytesIO(fp.read()))
            sdl_texture = sdl2.sdlimage.IMG_LoadTexture_RW(Renderer.sdl_renderer(), rw, freesrc=False)

        # Query texture for width and height
        width = c_int()
        height = c_int()
        sdl2.SDL_QueryTexture(sdl_texture, None, None, byref(width), byref(height))

        return Texture(width.value, height.value, sdl_texture, image_file.name)

    def set_scale_mode(self, scale_mode: ScaleMode) -> None:
        """ Set the texture scale mode. """
        self._scale_mode = scale_mode
        match scale_mode:
            case ScaleMode.NEAREST:
                sdl2.SDL_SetTextureScaleMode(self.sdl_texture, sdl2.SDL_ScaleModeNearest)
            case ScaleMode.LINEAR:
                sdl2.SDL_SetTextureScaleMode(self.sdl_texture, sdl2.SDL_ScaleModeLinear)
            case ScaleMode.BEST:
                sdl2.SDL_SetTextureScaleMode(self.sdl_texture, sdl2.SDL_ScaleModeBest)

    def set_blend_mode(self, blend_mode: BlendMode) -> None:
        """ Set the texture blend mode. """
        self._blend_mode = blend_mode
        match blend_mode:
            case BlendMode.NONE:
                sdl2.SDL_SetTextureBlendMode(self.sdl_texture, sdl2.SDL_BLENDMODE_NONE)
            case BlendMode.BLEND:
                sdl2.SDL_SetTextureBlendMode(self.sdl_texture, sdl2.SDL_BLENDMODE_BLEND)
            case BlendMode.ADD:
                sdl2.SDL_SetTextureBlendMode(self.sdl_texture, sdl2.SDL_BLENDMODE_ADD)
            case BlendMode.MOD:
                sdl2.SDL_SetTextureBlendMode(self.sdl_texture, sdl2.SDL_BLENDMODE_MOD)
            case BlendMode.MUL:
                sdl2.SDL_SetTextureBlendMode(self.sdl_texture, sdl2.SDL_BLENDMODE_MUL)
            case BlendMode.ALPHA_COMPOSITE:
                sdl2.SDL_SetTextureBlendMode(self.sdl_texture, POTION_BLENDMODE_ALPHA_COMPOSITE)

    def to_surface(self) -> sdl2.SDL_Surface:
        """ Convert the texture to a surface.
        Warning: This is a slow operation.
        """
        from potion.renderer import Renderer

        # Create surface
        surface = sdl2.SDL_CreateRGBSurfaceWithFormat(0, self.width, self.height, 32, sdl2.SDL_PIXELFORMAT_ARGB8888)

        # Render texture to temporary render target, and read it into the surface texture
        with Renderer.render_target(Texture.create_target(self.width, self.height)):
            Renderer.clear()
            Renderer.copy(
                texture=self,
                source_rect=None,
                destination_rect=None,
                rotation_angle=0,
                rotation_center=None,
                flip=0
            )
            sdl2.SDL_RenderReadPixels(
                Renderer.sdl_renderer(),
                None,
                sdl2.SDL_PIXELFORMAT_ARGB8888,
                surface.contents.pixels,
                surface.contents.pitch,
            )

        return surface
