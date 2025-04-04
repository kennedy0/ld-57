from __future__ import annotations

from typing import Type, TYPE_CHECKING

from potion.data_types.color import Color
from potion.data_types.point import Point

if TYPE_CHECKING:
    from potion.text import Glyph


class TextEffect:
    """ Applies a visual effect to Text. """

    __registry: dict[str, Type[TextEffect]] = {}

    def __str__(self) -> str:
        return f"TextEffect({self.tag()})"

    def __repr__(self) -> str:
        return str(self)

    @classmethod
    def register(cls) -> None:
        """ Register the text effect. """
        cls.__registry[cls.tag()] = cls

    @classmethod
    def get(cls, tag: str) -> Type[TextEffect] | None:
        """ Get a text effect from the registry. """
        return cls.__registry.get(tag)

    @classmethod
    def tag(cls) -> str:
        """ The name of the effect. """
        raise NotImplementedError

    @classmethod
    def glyph_offset(cls, glyph: Glyph) -> Point:
        """ Apply an additional offset to the glyph's position. """
        return Point.zero()

    @classmethod
    def glyph_color(cls, glyph: Glyph) -> Color:
        """ Set the color the glyph should be drawn as.
        Only RGB is considered - the Alpha value is not used.
        """
        return Color.white()

    @classmethod
    def glyph_opacity(cls, glyph: Glyph) -> int:
        """ Sets the opacity the glyph should be drawn at. """
        return 255
