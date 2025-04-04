from __future__ import annotations

import math
from typing import TYPE_CHECKING

from potion.bitmap_font import BitmapFont
from potion.content import Content
from potion.content_types.texture import Texture
from potion.data_types.blend_mode import BlendMode
from potion.data_types.color import Color
from potion.data_types.point import Point
from potion.data_types.rect import Rect
from potion.glyph import Glyph
from potion.log import Log
from potion.renderer import Renderer
from potion.text_effect import TextEffect
from potion.utilities import pmath

if TYPE_CHECKING:
    from potion.camera import Camera


ALIGN_CENTER = 0
ALIGN_LEFT = 1
ALIGN_RIGHT = 2
ALIGN_TOP = 3
ALIGN_BOTTOM = 4


class Text:
    """ Displays a string of text using a bitmap font. """
    def __init__(self, content_path: str) -> None:
        """ `content_path` is the path to the bitmap font texture file. """
        self._font_texture = Content.load_texture(content_path)
        self._font = BitmapFont.instance(content_path)
        self._text = ""
        self._width = 0
        self._height = 0
        self._lines = 0
        self._word_wrap = False
        self._max_line_width = 0
        self._tags_enabled = True
        self._effects_enabled = True
        self._typewriter_mode = False
        self._visible_characters = 0
        self._color = Color.white()
        self._opacity = 255

        # This texture is used as a cache so that each character doesn't have to be calculated/drawn each frame
        self._cache_texture = Texture.create_target(2, 2)
        self._cache_dirty = False
        self._cache_disabled = False
        Renderer.add_reset_callback(self._reset_cache_texture)

        # List of characters to be rendered in the text string
        self._glyphs: list[Glyph] = []
        self._end_glyph: Glyph | None = None

        # Text alignment
        self._horizontal_alignment = ALIGN_LEFT
        self._vertical_alignment = ALIGN_TOP
        self._alignment_offset = Point.zero()

    def __del__(self) -> None:
        Renderer.remove_reset_callback(self._reset_cache_texture)

    def __str__(self) -> str:
        character_limit = 25
        if len(self.text) > character_limit:
            return f"Text({self.text[:character_limit] + '...'})"
        else:
            return f"Text({self.text})"

    def __repr__(self) -> str:
        return str(self)

    @property
    def font(self) -> BitmapFont:
        """ The bitmap font used. """
        return self._font

    @property
    def text(self) -> str:
        """ The text to display. """
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        if value == self._text:
            return

        if not isinstance(value, str):
            value = str(value)

        self._text = value
        self._update_characters()

    @property
    def width(self) -> int:
        """ The width of the text. """
        return self._width

    @property
    def height(self) -> int:
        """ The height of the text. """
        return self._height

    @property
    def lines(self) -> int:
        """ The number of lines in the text. """
        return self._lines

    @property
    def alignment_offset(self) -> Point:
        """ The offset applied to the text position based on its alignment. """
        return self._alignment_offset

    @property
    def word_wrap(self) -> bool:
        """ If true, enables word wrap mode.
        In word wrap mode, the 'max_line_width' parameter controls the maximum width that a line can be before a line
        break is created.
        """
        return self._word_wrap

    @word_wrap.setter
    def word_wrap(self, value: bool) -> None:
        if value == self._word_wrap:
            return

        self._word_wrap = value
        self._update_characters()

    @property
    def max_line_width(self) -> int:
        """ In word wrap mode, this controls the maximum length a line can be before a line break is created. """
        return self._max_line_width

    @max_line_width.setter
    def max_line_width(self, value: int) -> None:
        if value == self._max_line_width:
            return

        self._max_line_width = value
        self._update_characters()

    @property
    def tags_enabled(self) -> bool:
        """ If True, angled brackets are used to signify text tags, and their contents will not be rendered.
        If False, angled brackets will be rendered as normal text
        """
        return self._tags_enabled

    @tags_enabled.setter
    def tags_enabled(self, value: bool) -> None:
        if value == self._tags_enabled:
            return

        self._tags_enabled = value
        self._update_characters()

    @property
    def effects_enabled(self) -> bool:
        return self._effects_enabled

    @effects_enabled.setter
    def effects_enabled(self, value: bool) -> None:
        if value == self._effects_enabled:
            return

        self._effects_enabled = value
        self._update_characters()

    @property
    def typewriter_mode(self) -> bool:
        """ If true, enables typewriter mode.
        In typewriter mode, the 'visible_characters' parameter controls the number of characters that are visible.
        """
        return self._typewriter_mode

    @typewriter_mode.setter
    def typewriter_mode(self, value: bool) -> None:
        if value == self._typewriter_mode:
            return

        self._typewriter_mode = value
        self._set_cache_dirty()

    @property
    def visible_characters(self) -> int:
        """ In typewriter mode, this controls the number of characters that are visible.
        Increasing the value over time creates a typewriter effect.
        """
        return self._visible_characters

    @visible_characters.setter
    def visible_characters(self, value: int) -> None:
        if value == self._visible_characters:
            return

        self._visible_characters = value
        self._set_cache_dirty()

    @property
    def color(self) -> Color:
        """ The default color of the text.
        Text effects may override this on a per-glyph basis.
        """
        return self._color

    @color.setter
    def color(self, value: Color) -> None:
        if value == self._color:
            return

        self._color = value
        self._set_cache_dirty()

    @property
    def opacity(self) -> int:
        """ The default opacity of the text.
        Text effects may override this on a per-glyph basis.
        """
        return self._opacity

    @opacity.setter
    def opacity(self, value: int) -> None:
        """ Opacity can be set as a 0-255 int value. """
        if value == self.opacity:
            return

        self._opacity = pmath.clamp(value, 0, 255)
        self._set_cache_dirty()

    def align_horizontal_left(self) -> None:
        """ Left align. """
        if self._horizontal_alignment != ALIGN_LEFT:
            self._horizontal_alignment = ALIGN_LEFT
            self._update_characters()

    def align_horizontal_center(self) -> None:
        """ Center align. """
        if self._horizontal_alignment != ALIGN_CENTER:
            self._horizontal_alignment = ALIGN_CENTER
            self._update_characters()

    def align_horizontal_right(self) -> None:
        """ Right align. """
        if self._horizontal_alignment != ALIGN_RIGHT:
            self._horizontal_alignment = ALIGN_RIGHT
            self._update_characters()

    def align_vertical_top(self) -> None:
        """ Top align. """
        if self._vertical_alignment != ALIGN_TOP:
            self._vertical_alignment = ALIGN_TOP
            self._update_characters()

    def align_vertical_center(self) -> None:
        """ Center align. """
        if self._vertical_alignment != ALIGN_CENTER:
            self._vertical_alignment = ALIGN_CENTER
            self._update_characters()

    def align_vertical_bottom(self) -> None:
        """ Bottom align. """
        if self._vertical_alignment != ALIGN_BOTTOM:
            self._vertical_alignment = ALIGN_BOTTOM
            self._update_characters()

    def glyph_count(self) -> int:
        """ Get the number of glyphs. """
        return len(self._glyphs)

    def glyph(self, glyph_index: int) -> Glyph:
        """ Get the glyph at a given index. """
        # Return the end glyph if we're trying to get a glyph at an index higher than the text length
        if glyph_index >= len(self._glyphs):
            return self._end_glyph

        return self._glyphs[glyph_index]

    def end_glyph(self) -> Glyph | None:
        """ Get the 'null' glyph that ends the text.
        This is not drawn, but is used as a utility when getting the text metrics.
        """
        return self._end_glyph

    def glyph_position(self, glyph: Glyph) -> Point:
        """ Calculate the position that the glyph should be drawn at. """
        # Add the character offset to the text anchor position
        glyph_x = glyph.destination_offset_x
        glypy_y = glyph.destination_offset_y

        # Add text effect offset
        if glyph.tag and self.effects_enabled:
            if text_effect := TextEffect.get(glyph.tag):
                glyph_offset = text_effect.glyph_offset(glyph)
                glyph_x += glyph_offset.x
                glypy_y += glyph_offset.y

        return Point(glyph_x, glypy_y)

    def glyph_rect(self, glyph: Glyph) -> Rect:
        """ Calculate the rect that the glyph should be drawn at. """
        glyph_position = self.glyph_position(glyph)
        return Rect(glyph_position.x, glyph_position.y, glyph.source_rect.width, glyph.source_rect.height)

    def glyph_color(self, glyph: Glyph) -> Color:
        """ Get the color that the glyph should be drawn as. """
        if glyph.tag and self.effects_enabled:
            if text_effect := TextEffect.get(glyph.tag):
                return text_effect.glyph_color(glyph)
        else:
            return self.color

    def glyph_opacity(self, glyph: Glyph) -> int:
        """ Get the opacity that the glyph should be drawn at. """
        if glyph.tag and self.effects_enabled:
            if text_effect := TextEffect.get(glyph.tag):
                return text_effect.glyph_opacity(glyph)
        else:
            return self.opacity

    def glyph_at(self, position: Point) -> Glyph | None:
        """ Get the glyph at a given position. """
        for i, glyph in enumerate(self._glyphs):
            if self.glyph_rect(glyph).contains_point(position):
                return glyph

    def line_start(self, line: int) -> int:
        """ Get the glyph index at the start of a line. """
        for glyph in self._glyphs + [self._end_glyph]:
            if glyph.line == line:
                return glyph.index

        return 0

    def line_end(self, line: int) -> int:
        """ Get the glyph index at the end of a line. """
        for glyph in reversed(self._glyphs + [self._end_glyph]):
            if glyph.line == line:
                return glyph.index

        return 0

    def draw(self, camera: Camera, position: Point) -> None:
        """ Draw the text at a given position. """
        # Update the cache
        if self._cache_dirty or self._cache_disabled:
            self._draw_to_cache()

        # Convert world position to render position
        render_position = camera.world_to_render_position(position) + self._alignment_offset
        destination = Rect(render_position.x, render_position.y, self.width, self.height)

        # Render texture
        Renderer.copy(
            texture=self._cache_texture,
            source_rect=None,
            destination_rect=destination,
            rotation_angle=0,
            rotation_center=None,
            flip=0
        )

    def _reset_cache_texture(self) -> None:
        """ Reset the cache texture. """
        self._create_cache_texture()
        self._set_cache_dirty()

    def _create_cache_texture(self) -> None:
        """ Create the cache texture. """
        self._cache_texture = Texture.create_target(self.width, self.height)
        self._cache_texture.set_blend_mode(BlendMode.BLEND)

    def _set_cache_dirty(self) -> None:
        """ Set the cache as 'dirty' so that it's redrawn. """
        self._cache_dirty = True

    def _draw_to_cache(self) -> None:
        """ Draw the text to the render texture cache. """
        # Clear the dirty flag
        self._cache_dirty = False

        # Recreate the texture if the size changed
        if self._cache_texture.width != self.width or self._cache_texture.height != self.height:
            self._create_cache_texture()

        with Renderer.render_target(self._cache_texture):
            Renderer.clear()

            for i, glyph in enumerate(self._glyphs):
                if self.typewriter_mode and i >= self.visible_characters:
                    break

                self._draw_glyph(glyph)

    def _draw_glyph(self, glyph: Glyph) -> None:
        """ Draw a glyph. """
        # Set destination
        destination = self.glyph_rect(glyph)

        # Don't draw newlines
        if glyph.character == '\n':
            return

        # Set color
        glyph_color = self.glyph_color(glyph)
        Renderer.set_texture_color_mod(self._font_texture, glyph_color)

        # Set opacity
        glyph_opacity = self.glyph_opacity(glyph)
        Renderer.set_texture_alpha_mod(self._font_texture, glyph_opacity)

        # Render texture
        Renderer.copy(
            texture=self._font_texture,
            source_rect=glyph.source_rect,
            destination_rect=destination,
            rotation_angle=0,
            rotation_center=None,
            flip=0
        )

        # Clear color and opacity
        Renderer.clear_texture_color_mod(self._font_texture)
        Renderer.clear_texture_alpha_mod(self._font_texture)

    def _update_characters(self) -> None:
        """ Update the character source positions and destination offsets when the text changes """
        # Dirty the cache
        self._set_cache_dirty()
        self._cache_disabled = False

        # Reset text data
        self._width = 0
        self._height = 0
        self._lines = 0
        self._glyphs.clear()

        # The current index of the source text that the cursor is at
        cursor = 0

        # The line that the current glyph will be drawn on
        line = 0

        # The column number of the glyph
        column = 0

        # The X and Y position that the current glyph will be drawn at
        x = 0
        y = 0

        # The current tag that we're in
        tag = None

        while cursor < len(self.text):
            # Get the current character
            char = self.text[cursor]

            # Handle newline characters
            if char == '\n':
                # Use space as the visible glyph (although it won't be drawn)
                source_rect = self._font.get_source_rect(' ')
                glyph = Glyph(
                    character=char,
                    source_rect=source_rect,
                    destination_offset_x=x,
                    destination_offset_y=y,
                    source_index=cursor,
                    index=len(self._glyphs),
                    line=line,
                    column=column,
                    tag=tag,
                )
                self._glyphs.append(glyph)

                x = 0
                y += self._font.line_height
                line += 1
                column = 0
                cursor += 1
                continue

            # Handle tags
            if self._is_cursor_at_start_of_tag(cursor):
                # Disable the cache
                self._cache_disabled = True

                # Read current tag
                tag_str = self._read_tag(cursor)

                # Set (or clear) the current tag
                if len(tag_str) and tag_str[0] == '/':
                    tag = None
                else:
                    tag = tag_str

                # Advance cursor to end of tag
                cursor_advance = len(tag_str) + 2
                cursor += cursor_advance
                continue

            # Handle word wrap
            if x > 0:
                if self.word_wrap and self._is_cursor_at_start_of_new_word(cursor):
                    # Get the next word.
                    # Spaces are treated as a complete word, otherwise they would never wrap
                    if char.isspace():
                        next_word = char
                    else:
                        next_word = self._get_next_word(cursor)

                    # Do a carriage return if the next word would exceed the max line width
                    next_word_width = self._get_word_width(next_word)
                    if x + next_word_width > self.max_line_width:
                        x = 0
                        y += self._font.line_height
                        line += 1
                        column = 0

            # Create glyph for character
            source_rect = self._font.get_source_rect(char)
            glyph = Glyph(
                character=char,
                source_rect=source_rect,
                destination_offset_x=x,
                destination_offset_y=y,
                source_index=cursor,
                index=len(self._glyphs),
                line=line,
                column=column,
                tag=tag,
            )
            self._glyphs.append(glyph)

            # Advance the cursor
            x += source_rect.width
            column += 1
            cursor += 1

        # Create the end glyph
        source_rect = self._font.get_source_rect(' ')
        self._end_glyph = Glyph(
            character='',
            source_rect=source_rect,
            destination_offset_x=x,
            destination_offset_y=y,
            source_index=cursor,
            index=len(self._glyphs),
            line=line,
            column=column,
            tag=tag,
        )

        # Now that all glyphs have been generated, alignment and text size can be calculated
        self._lines = line + 1
        self._height = self._lines * self._font.line_height
        if len(self._glyphs):
            self._apply_horizontal_alignment()
            self._update_width()
            self._update_alignment_offset()

    def _is_cursor_at_start_of_new_word(self, cursor: int) -> bool:
        """ Check if the cursor is at the start of a new word. """
        # If this is the very first character, we never want this to be true, otherwise it would always start by
        #   inserting a newline.
        if cursor == 0:
            return False

        previous_char = self.text[cursor-1]

        if previous_char.isspace():
            return True
        else:
            return False

    def _get_next_word(self, cursor: int) -> str:
        """ Find the next word in the text.
        This assumes the cursor position is on the first character of the next word.
        """
        text_remainder = self.text[cursor:]
        next_word = text_remainder.split(maxsplit=1)[0]
        return next_word

    def _get_word_width(self, word: str) -> int:
        """ Calculate the width in pixels of a word. """
        word_width = 0
        for char in word:
            word_width += self._font.get_source_rect(char).width

        return word_width

    def _is_cursor_at_start_of_tag(self, cursor: int) -> bool:
        """ Check if the cursor is at the start of a tag. """
        if not self._tags_enabled:
            return False

        current_char = self.text[cursor]
        if cursor > 0:
            previous_char = self.text[cursor - 1]
        else:
            previous_char = ''

        if current_char == '<':
            return True
        else:
            return False

    def _read_tag(self, cursor: int) -> str:
        """ Read a tag and return its value.
        This assumes the cursor position is on the left angle bracket of the tag.
        """
        i = cursor + 1
        tag = ""
        while (char := self.text[i]) != '>':
            tag += char
            i += 1
        return tag

    def _apply_horizontal_alignment(self) -> None:
        """ Adjust the horizontal position of each character to align each line. """
        # Get the number of lines
        num_lines = self._glyphs[-1].line + 1

        # Initialize line widths
        line_widths = []
        for _ in range(num_lines):
            line_widths.append(0)

        # Find the width of each line
        for char in self._glyphs:
            x = char.destination_offset_x + char.source_rect.width
            if x > line_widths[char.line]:
                line_widths[char.line] = x

        # Get the max line width
        max_line_width = max(line_widths)

        # Calculate each line offset based on alignment
        line_offsets = []
        for line_width in line_widths:
            if self._horizontal_alignment == ALIGN_LEFT:
                offset_x = 0
            elif self._horizontal_alignment == ALIGN_CENTER:
                offset_x = (max_line_width - line_width) // 2
            elif self._horizontal_alignment == ALIGN_RIGHT:
                offset_x = math.ceil(max_line_width - line_width)
            else:
                offset_x = 0
                Log.error(f"Invalid horizontal alignment: {self._horizontal_alignment}")

            line_offsets.append(offset_x)

        # Apply alignment offset to characters
        for char in self._glyphs:
            line_offset = line_offsets[char.line]
            char.destination_offset_x += line_offset

    def _update_width(self) -> None:
        """ Update the width of the text by finding the min and max X positions of all characters. """
        x_min = None
        x_max = None

        for char in self._glyphs:
            # Skip newlines
            if char == '\n':
                continue

            left = char.destination_offset_x
            right = char.destination_offset_x + char.source_rect.width
            if x_min is None or left < x_min:
                x_min = left
            if x_max is None or right > x_max:
                x_max = right

        self._width = x_max - x_min

    # noinspection DuplicatedCode
    def _update_alignment_offset(self) -> None:
        """ Update the offsets based on the alignment. """
        if self._horizontal_alignment == ALIGN_LEFT:
            x = 0
        elif self._horizontal_alignment == ALIGN_CENTER:
            x = -1 * self._width // 2
        elif self._horizontal_alignment == ALIGN_RIGHT:
            x = -1 * self.width + 1
        else:
            x = 0
            Log.error(f"Invalid horizontal alignment: {self._horizontal_alignment}")

        if self._vertical_alignment == ALIGN_TOP:
            y = 0
        elif self._vertical_alignment == ALIGN_CENTER:
            y = -1 * self._height // 2
        elif self._vertical_alignment == ALIGN_BOTTOM:
            y = -1 * self.height + 1
        else:
            y = 0
            Log.error(f"Invalid vertical alignment: {self._vertical_alignment}")

        self._alignment_offset = Point(x, y)
