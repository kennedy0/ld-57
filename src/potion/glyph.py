from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from potion.data_types.rect import Rect


@dataclass
class Glyph:
    """ Stores data about a renderable character in a text string. """
    # The character from the source text that will be rendered.
    character: str

    # The source rect of the glyph in the bitmap font texture.
    source_rect: Rect

    # The offset to draw the glyph at, relative to the starting point of the text string.
    destination_offset_x: int
    destination_offset_y: int

    # The position in the source text that this glyph appears.
    source_index: int

    # The position in the rendered text that this glyph appears.
    # This is NOT the same as the source index.
    # Some source characters (e.g. tags) don't get rendered as glyphs, so this number may be lower than the
    # source_index value.
    index: int

    # The line number that the glyph is drawn on.
    line: int

    # The column number that the glyph is drawn on.
    column: int

    # An optional tag.
    tag: str | None

    def __str__(self) -> str:
        return f"Glyph({self.character})"

    def __repr__(self) -> str:
        return str(self)
