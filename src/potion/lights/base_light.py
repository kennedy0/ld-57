from potion.data_types.color import Color
from potion.utilities import pmath


class BaseLight:
    """ Light base class. """
    def __init__(self) -> None:
        self._intensity = 1
        self._glow_intensity = 0
        self._color = Color.white()

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(intensity={self._intensity}, glow_intensity={self._glow_intensity}, color={self._color})"

    def __repr__(self) -> str:
        return str(self)

    @property
    def intensity(self) -> float:
        """ The intensity of the light. """
        return self._intensity

    @intensity.setter
    def intensity(self, value: float) -> None:
        """ Set the intensity of the light (0-1 range). """
        self._intensity = pmath.clamp(value, 0, 1)

    @property
    def glow_intensity(self) -> float:
        """ The glow intensity of the light. """
        return self._glow_intensity

    @glow_intensity.setter
    def glow_intensity(self, value: float) -> None:
        """ Set the glow intensity of the light (0-1 range). """
        self._glow_intensity = pmath.clamp(value, 0, 1)

    @property
    def color(self) -> Color:
        """ The color of the light. """
        return self._color

    @color.setter
    def color(self, value: Color) -> None:
        """ Set the color of the light.
        The alpha value is not used; set the `intensity` instead.
        """
        self._color = value
