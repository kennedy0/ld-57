from __future__ import annotations

import sdl2

from potion.data_types.vector2 import Vector2
from potion.utilities import pmath


class GameController:
    """ Abstract controller device that is similar to an Xbox controller.  """
    def __init__(self, device_index: int) -> None:
        self._sdl_controller = sdl2.SDL_GameControllerOpen(device_index)
        self._joystick_instance_id = sdl2.SDL_JoystickGetDeviceInstanceID(device_index)

        self._buttons: set = set()
        self._current_buttons: set = set()
        self._previous_buttons: set = set()

        self._axes: dict[int: int] = {}

        self._digital_axes_positive: set = set()
        self._current_digital_axes_positive: set = set()
        self._previous_digital_axes_positive: set = set()

        self._digital_axes_negative: set = set()
        self._current_digital_axes_negative: set = set()
        self._previous_digital_axes_negative: set = set()

        # Axis dead zones
        self._left_analog_stick_dead_zone = 10000
        self._right_analog_stick_dead_zone = 10000
        self._left_trigger_dead_zone = 10000
        self._right_trigger_dead_zone = 10000

        # This is the threshold that an axis value must pass before a digital axis is considered pressed
        self._digital_axis_threshold: int = 16000

    def __str__(self) -> str:
        return f"Controller({self.name})"

    def __repr__(self) -> str:
        return str(self)

    @property
    def sdl_controller(self) -> int:
        """ Pointer to the SDL controller. """
        return self._sdl_controller

    @property
    def joystick_instance_id(self) -> int:
        """ The joystick instance ID of the controller. """
        return self._joystick_instance_id

    @property
    def name(self) -> str | None:
        name = sdl2.SDL_GameControllerName(self.sdl_controller)
        if isinstance(name, bytes):
            name = name.decode("utf-8")
            return name

    def update(self):
        """ Update the current input state. """
        self._previous_buttons = self._current_buttons.copy()
        self._current_buttons = self._buttons.copy()

        self._previous_digital_axes_positive = self._current_digital_axes_positive.copy()
        self._current_digital_axes_positive = self._digital_axes_positive.copy()

        self._previous_digital_axes_negative = self._current_digital_axes_negative.copy()
        self._current_digital_axes_negative = self._digital_axes_negative.copy()

    def register_button_down(self, button: int) -> None:
        """ Indicate that a button on the controller has been pressed. """
        self._buttons.add(button)

    def register_button_up(self, button: int) -> None:
        """ Indicate that a button on the controller has been released. """
        self._buttons.remove(button)

    def register_axis_motion(self, axis: int, value: int) -> None:
        """ Indicate that an axis value on the controller has changed. """
        # Real axis value
        self._axes[axis] = value

        # Digital axis value
        if abs(value) < self._digital_axis_threshold:
            value = 0

        if value == 0:
            if axis in self._digital_axes_positive:
                self._digital_axes_positive.remove(axis)
            if axis in self._digital_axes_negative:
                self._digital_axes_negative.remove(axis)
        elif value > 0:
            self._digital_axes_positive.add(axis)
            if axis in self._digital_axes_negative:
                self._digital_axes_negative.remove(axis)
        elif value < 0:
            self._digital_axes_negative.add(axis)
            if axis in self._digital_axes_positive:
                self._digital_axes_positive.remove(axis)

    def get_button(self, button: int) -> bool:
        """ Check if a button is pressed. """
        return button in self._buttons

    def get_button_down(self, button: int) -> bool:
        """ Check if a button was pressed this frame. """
        return button in self._current_buttons and button not in self._previous_buttons

    def get_button_up(self, button: int) -> bool:
        """ Check if a button was released this frame. """
        return button not in self._current_buttons and button in self._previous_buttons

    def get_axis(self, axis: int) -> int:
        """ Get an axis's raw value.
        This will be range [-32768, 32767] for analog sticks and [0, 32767] for triggers.
        """
        return self._axes.get(axis, 0)

    def get_digital_axis(self, axis: int, direction: int) -> bool:
        """ Check if the digital representation of an axis is 'pressed'.
        'direction' determines whether the positive or negative axis direction is used, and should be either -1 or 1.
        """
        if direction < 0:
            return axis in self._digital_axes_negative
        else:
            return axis in self._digital_axes_positive

    def get_digital_axis_down(self, axis: int, direction: int) -> bool:
        """ Check if the digital representation of an axis was 'pressed' this frame.
        'direction' determines whether the positive or negative axis direction is used, and should be either -1 or 1.
        """
        if direction < 0:
            return axis in self._current_digital_axes_negative and axis not in self._previous_digital_axes_negative
        else:
            return axis in self._current_digital_axes_positive and axis not in self._previous_digital_axes_positive

    def get_digital_axis_up(self, axis: int, direction: int) -> bool:
        """ Check if the digital representation of an axis was 'released' this frame.
        'direction' determines whether the positive or negative axis direction is used, and should be either -1 or 1.
        """
        if direction < 0:
            return axis not in self._current_digital_axes_negative and axis in self._previous_digital_axes_negative
        else:
            return axis not in self._current_digital_axes_positive and axis in self._previous_digital_axes_positive

    def get_axis_left_x(self) -> float:
        """ Get the left analog stick's X axis value in a [-1, 1] range. """
        axis = self.get_axis(sdl2.SDL_CONTROLLER_AXIS_LEFTX)
        return self._remap_analog_axis(axis, self._left_analog_stick_dead_zone)

    def get_axis_left_y(self) -> float:
        """ Get the left analog stick's Y axis value in a [-1, 1] range. """
        axis = self.get_axis(sdl2.SDL_CONTROLLER_AXIS_LEFTY)
        return self._remap_analog_axis(axis, self._left_analog_stick_dead_zone)

    def get_axis_right_x(self) -> float:
        """ Get the right analog stick's X axis value in a [-1, 1] range. """
        axis = self.get_axis(sdl2.SDL_CONTROLLER_AXIS_RIGHTX)
        return self._remap_analog_axis(axis, self._right_analog_stick_dead_zone)

    def get_axis_right_y(self) -> float:
        """ Get the right analog stick's Y axis value in a [-1, 1] range. """
        axis = self.get_axis(sdl2.SDL_CONTROLLER_AXIS_RIGHTY)
        return self._remap_analog_axis(axis, self._right_analog_stick_dead_zone)

    def get_left_analog_stick(self) -> Vector2:
        """ Get the left analog stick's value. """
        return Vector2(self.get_axis_left_x(), self.get_axis_left_y())

    def get_right_analog_stick(self) -> Vector2:
        """ Get the right analog stick's value. """
        return Vector2(self.get_axis_right_x(), self.get_axis_right_y())

    def get_left_trigger(self) -> float:
        """ Get the left trigger's value in a [0, 1] range. """
        axis = self.get_axis(sdl2.SDL_CONTROLLER_AXIS_TRIGGERLEFT)
        return self._remap_trigger_axis(axis, self._left_trigger_dead_zone)

    def get_right_trigger(self) -> float:
        """ Get the right trigger's value in a [0, 1] range. """
        axis = self.get_axis(sdl2.SDL_CONTROLLER_AXIS_TRIGGERRIGHT)
        return self._remap_trigger_axis(axis, self._right_trigger_dead_zone)

    @staticmethod
    def _remap_analog_axis(value: int, dead_zone: int) -> float:
        """ Remap an analog stick axis value from [-32768, 32767] to [-1.0, 1.0]. """
        if abs(value) < dead_zone:
            value = 0

        if value == 0:
            return 0

        return pmath.remap(value, -32768, 32767, -1.0, 1.0)

    @staticmethod
    def _remap_trigger_axis(value: int, dead_zone: int) -> float:
        """ Remap a trigger axis value from [0, 32767] to [0, 1.0]. """
        if abs(value) < dead_zone:
            value = 0

        if value == 0:
            return 0

        return pmath.remap(value, 0, 32767, 0.0, 1.0)

    def close(self) -> None:
        """" Close the controller. """
        sdl2.SDL_GameControllerClose(self.sdl_controller)
