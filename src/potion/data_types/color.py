from __future__ import annotations

import colorsys
import random
import re

from potion.log import Log
from potion.utilities import pmath


_HEX_COLOR_RE = re.compile(r"^#?(?P<r>[0-9a-f]{2})(?P<g>[0-9a-f]{2})(?P<b>[0-9a-f]{2})$", re.I)


class Color:
    """ A 32-bit color. """
    def __init__(self, r: int, g: int, b: int, a: int = 255):
        self._r = int(pmath.clamp(r, 0, 255))
        self._g = int(pmath.clamp(g, 0, 255))
        self._b = int(pmath.clamp(b, 0, 255))
        self._a = int(pmath.clamp(a, 0, 255))

    def __str__(self) -> str:
        return f"Color({self.r}, {self.g}, {self.b}, {self.a})"

    def __repr__(self) -> str:
        return str(self)

    def __len__(self):
        return self.to_tuple().__len__()

    def __getitem__(self, item):
        return self.to_tuple().__getitem__(item)

    def __iter__(self):
        return iter(self.to_tuple())

    def __eq__(self, other: Color) -> bool:
        if not isinstance(other, Color):
            return False

        return self.r == other.r and self.g == other.g and self.b == other.b and self.a == other.a
    
    @property
    def r(self) -> int:
        return self._r

    @r.setter
    def r(self, value: int) -> None:
        self._r = value

    @property
    def g(self) -> int:
        return self._g

    @g.setter
    def g(self, value: int) -> None:
        self._g = value

    @property
    def b(self) -> int:
        return self._b

    @b.setter
    def b(self, value: int) -> None:
        self._b = value

    @property
    def a(self) -> int:
        return self._a

    @a.setter
    def a(self, value: int) -> None:
        self._a = value

    def to_tuple(self) -> tuple[int, int, int, int]:
        """ Return a copy of the color as a tuple. """
        return self.r, self.g, self.b, self.a

    def hsv(self) -> tuple[int, int, int]:
        """ Get the HSV values. """
        return self.rgb_to_hsv(self.r, self.g, self.b)

    def hue(self) -> int:
        """ Get the hue (0-360 range). """
        return self.hsv()[0]

    def saturation(self) -> int:
        """ Get the saturation (0-100 range). """
        return self.hsv()[1]

    def value(self) -> int:
        """ Get the value (0-100 range). """
        return self.hsv()[2]

    def hex(self) -> str:
        """ Get the hex code of a color. """
        return f"{self.r:02x}{self.g:02x}{self.b:02x}"

    @classmethod
    def black(cls) -> Color:
        return Color(0, 0, 0, 255)

    @classmethod
    def white(cls) -> Color:
        return Color(255, 255, 255, 255)

    @classmethod
    def gray(cls) -> Color:
        return Color(128, 128, 128, 255)

    @classmethod
    def red(cls) -> Color:
        return Color(255, 0, 0, 255)

    @classmethod
    def green(cls) -> Color:
        return Color(0, 255, 0, 255)

    @classmethod
    def blue(cls) -> Color:
        return Color(0, 0, 255, 255)

    @classmethod
    def cyan(cls) -> Color:
        return Color(0, 255, 255, 255)

    @classmethod
    def magenta(cls) -> Color:
        return Color(255, 0, 255, 255)

    @classmethod
    def yellow(cls) -> Color:
        return Color(255, 255, 0, 255)

    @classmethod
    def orange(cls) -> Color:
        return Color(255, 128, 0, 255)

    @classmethod
    def transparent(cls) -> Color:
        return Color(0, 0, 0, 0)

    @classmethod
    def random(cls, saturation: int | None = None, value: int | None = None) -> Color:
        """ Generates a random color.

        Saturation and value can be specified (0-100 range) to prevent those values from being randomly generated.
        Allowing randomness in saturation and brightness often produces muddy results.

        Alpha is always 255.
        """
        # Set HSV values
        hue = random.randint(0, 360)

        if saturation is not None:
            saturation = pmath.clamp(saturation, 0, 100)
        else:
            saturation = random.randint(0, 100)

        if value is not None:
            value = pmath.clamp(value, 0, 100)
        else:
            value = random.randint(0, 100)

        # Convert to color
        color = cls.from_hsv(hue, saturation, value)
        return color

    @classmethod
    def lerp(cls, color_a: Color, color_b: Color, t: float) -> Color:
        """ Linearly interpolate between 2 colors. """
        r = int(pmath.lerp(color_a.r, color_b.r, t))
        g = int(pmath.lerp(color_a.g, color_b.g, t))
        b = int(pmath.lerp(color_a.b, color_b.b, t))
        a = int(pmath.lerp(color_a.a, color_b.a, t))
        return cls(r, g, b, a)

    @classmethod
    def from_hsv(cls, h: int, s: int, v: int) -> Color:
        """ Create a color from HSV values.
        Hue is 0-360 range.
        Saturation and value are 0-100 range.
        Alpha will always be 255.
        """
        r, g, b = cls.hsv_to_rgb(h, s, v)
        return cls(r, g, b)

    @classmethod
    def from_hex(cls, hex_code: str) -> Color:
        """ Create a color from a hex code.
        Hex code must be in the format: #RRGGBB
        Alpha will always be 255.
        """
        match = _HEX_COLOR_RE.match(hex_code)
        if not match:
            color = cls.black()
            Log.error(f"Invalid color hex code: {hex_code}; Defaulting to {color}")
            return color

        r_hex = match.group('r')
        g_hex = match.group('g')
        b_hex = match.group('b')

        r = int(f"0x{r_hex}", 0)
        g = int(f"0x{g_hex}", 0)
        b = int(f"0x{b_hex}", 0)

        return cls(r, g, b)

    @classmethod
    def from_int(cls, value: int) -> Color:
        """ Create a color from an integer value.
        The integer value is assumed to be the base-10 of a hex code.
        """
        hex_code = f"#{value:06x}"
        return cls.from_hex(hex_code)

    @staticmethod
    def rgb_to_hsv(r: int, g: int, b: int) -> tuple[int, int, int]:
        """ Convert RGB values to HSV values. """
        # Convert RGB to float
        r /= 255
        g /= 255
        b /= 255

        # Convert to HSV float values
        h, s, v = colorsys.rgb_to_hsv(r, g, b)

        # Convert HSV to int
        h = int(h * 360)
        s = int(s * 100)
        v = int(v * 100)

        return h, s, v

    @staticmethod
    def hsv_to_rgb(h: int, s: int, v: int) -> tuple[int, int, int]:
        """ Convert HSV values to RGB values.
        Hue value is 0-360 range, but wraps around if greater than 360.
        Saturation and value are 0-100 range.
        RGB values are 0-255 range.
        """
        # Convert HSV to float
        h %= 360
        h /= 360
        s /= 100
        v /= 100

        # Convert to RGB float values
        r, g, b = colorsys.hsv_to_rgb(h, s, v)

        # Convert to RGB int values
        r = int(r * 255)
        g = int(g * 255)
        b = int(b * 255)

        return r, g, b
