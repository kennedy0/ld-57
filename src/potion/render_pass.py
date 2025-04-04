from potion.content_types.texture import Texture, BlendMode
from potion.data_types.color import Color
from potion.renderer import Renderer


class RenderPass:
    def __init__(self, name: str) -> None:
        self._name = name
        self._texture = Texture.create_target(2, 2)
        self._texture.set_blend_mode(BlendMode.ALPHA_COMPOSITE)
        self._blend_mode = self._texture.blend_mode
        self._clear_color = Color.transparent()

    def __str__(self) -> str:
        return f"RenderPass({self.name})"

    def __repr__(self) -> str:
        return str(self)

    @property
    def name(self) -> str:
        """ The name of the render pass. """
        return self._name

    @property
    def texture(self) -> Texture:
        """ The texture that the render pass is drawn to. """
        return self._texture

    def set_blend_mode(self, blend_mode: BlendMode) -> None:
        """ Set the texture blend mode. """
        self._blend_mode = blend_mode
        self._texture.set_blend_mode(blend_mode)

    def set_clear_color(self, color: Color) -> None:
        """ Set the clear color of the render pass."""
        self._clear_color = color

    def create_texture(self, width: int, height: int) -> None:
        """ Create the texture. """
        self._texture = Texture.create_target(width, height)
        self._texture.set_blend_mode(self._blend_mode)

    def clear(self) -> None:
        """ Clear the texture. """
        with Renderer.render_target(self._texture):
            Renderer.clear(self._clear_color)
