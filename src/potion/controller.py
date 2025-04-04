from __future__ import annotations

from typing import TYPE_CHECKING

import sdl2

from potion.data_types.vector2 import Vector2
from potion.input_manager import InputManager

if TYPE_CHECKING:
    from potion.game_controller import GameController


class Controller:
    """ Get controller input.
    For all methods, the controller's joystick instance id is an optional parameter.
    If it is not provided, the current active joystick will be used.
    """
    @classmethod
    def all_controllers(cls) -> tuple[GameController]:
        """ Get a list of all game controllers. """
        return InputManager.get_all_controllers()

    @classmethod
    def active_controller(cls) -> GameController | None:
        """ Get the active game controller. """
        return InputManager.get_active_controller()

    @classmethod
    def get_button(cls, button: int, controller_id: int | None = None) -> bool:
        """ Check if a button is pressed. """
        if controller := cls._get_controller(controller_id):
            return controller.get_button(button)
        return False

    @classmethod
    def get_button_down(cls, button: int, controller_id: int | None = None) -> bool:
        """ Check if a button was pressed this frame. """
        if controller := cls._get_controller(controller_id):
            return controller.get_button_down(button)
        return False

    @classmethod
    def get_button_up(cls, button: int, controller_id: int | None = None) -> bool:
        """ Check if a button was released this frame. """
        if controller := cls._get_controller(controller_id):
            return controller.get_button_up(button)
        return False

    @classmethod
    def get_a_button(cls) -> bool:
        return cls.get_button(sdl2.SDL_CONTROLLER_BUTTON_A)

    @classmethod
    def get_a_button_down(cls) -> bool:
        return cls.get_button_down(sdl2.SDL_CONTROLLER_BUTTON_A)

    @classmethod
    def get_a_button_up(cls) -> bool:
        return cls.get_button_up(sdl2.SDL_CONTROLLER_BUTTON_A)

    @classmethod
    def get_b_button(cls) -> bool:
        return cls.get_button(sdl2.SDL_CONTROLLER_BUTTON_B)

    @classmethod
    def get_b_button_down(cls) -> bool:
        return cls.get_button_down(sdl2.SDL_CONTROLLER_BUTTON_B)

    @classmethod
    def get_b_button_up(cls) -> bool:
        return cls.get_button_up(sdl2.SDL_CONTROLLER_BUTTON_B)

    @classmethod
    def get_x_button(cls) -> bool:
        return cls.get_button(sdl2.SDL_CONTROLLER_BUTTON_X)

    @classmethod
    def get_x_button_down(cls) -> bool:
        return cls.get_button_down(sdl2.SDL_CONTROLLER_BUTTON_X)

    @classmethod
    def get_x_button_up(cls) -> bool:
        return cls.get_button_up(sdl2.SDL_CONTROLLER_BUTTON_X)

    @classmethod
    def get_y_button(cls) -> bool:
        return cls.get_button(sdl2.SDL_CONTROLLER_BUTTON_Y)

    @classmethod
    def get_y_button_down(cls) -> bool:
        return cls.get_button_down(sdl2.SDL_CONTROLLER_BUTTON_Y)

    @classmethod
    def get_y_button_up(cls) -> bool:
        return cls.get_button_up(sdl2.SDL_CONTROLLER_BUTTON_Y)

    @classmethod
    def get_back_button(cls) -> bool:
        return cls.get_button(sdl2.SDL_CONTROLLER_BUTTON_BACK)

    @classmethod
    def get_back_button_down(cls) -> bool:
        return cls.get_button_down(sdl2.SDL_CONTROLLER_BUTTON_BACK)

    @classmethod
    def get_back_button_up(cls) -> bool:
        return cls.get_button_up(sdl2.SDL_CONTROLLER_BUTTON_BACK)

    @classmethod
    def get_guide_button(cls) -> bool:
        return cls.get_button(sdl2.SDL_CONTROLLER_BUTTON_GUIDE)

    @classmethod
    def get_guide_button_down(cls) -> bool:
        return cls.get_button_down(sdl2.SDL_CONTROLLER_BUTTON_GUIDE)

    @classmethod
    def get_guide_button_up(cls) -> bool:
        return cls.get_button_up(sdl2.SDL_CONTROLLER_BUTTON_GUIDE)

    @classmethod
    def get_start_button(cls) -> bool:
        return cls.get_button(sdl2.SDL_CONTROLLER_BUTTON_START)

    @classmethod
    def get_start_button_down(cls) -> bool:
        return cls.get_button_down(sdl2.SDL_CONTROLLER_BUTTON_START)

    @classmethod
    def get_start_button_up(cls) -> bool:
        return cls.get_button_up(sdl2.SDL_CONTROLLER_BUTTON_START)

    @classmethod
    def get_left_stick_button(cls) -> bool:
        return cls.get_button(sdl2.SDL_CONTROLLER_BUTTON_LEFTSTICK)

    @classmethod
    def get_left_stick_button_down(cls) -> bool:
        return cls.get_button_down(sdl2.SDL_CONTROLLER_BUTTON_LEFTSTICK)

    @classmethod
    def get_left_stick_button_up(cls) -> bool:
        return cls.get_button_up(sdl2.SDL_CONTROLLER_BUTTON_LEFTSTICK)

    @classmethod
    def get_right_stick_button(cls) -> bool:
        return cls.get_button(sdl2.SDL_CONTROLLER_BUTTON_RIGHTSTICK)

    @classmethod
    def get_right_stick_button_down(cls) -> bool:
        return cls.get_button_down(sdl2.SDL_CONTROLLER_BUTTON_RIGHTSTICK)

    @classmethod
    def get_right_stick_button_up(cls) -> bool:
        return cls.get_button_up(sdl2.SDL_CONTROLLER_BUTTON_RIGHTSTICK)

    @classmethod
    def get_left_shoulder_button(cls) -> bool:
        return cls.get_button(sdl2.SDL_CONTROLLER_BUTTON_LEFTSHOULDER)

    @classmethod
    def get_left_shoulder_button_down(cls) -> bool:
        return cls.get_button_down(sdl2.SDL_CONTROLLER_BUTTON_LEFTSHOULDER)

    @classmethod
    def get_left_shoulder_button_up(cls) -> bool:
        return cls.get_button_up(sdl2.SDL_CONTROLLER_BUTTON_LEFTSHOULDER)

    @classmethod
    def get_right_shoulder_button(cls) -> bool:
        return cls.get_button(sdl2.SDL_CONTROLLER_BUTTON_RIGHTSHOULDER)

    @classmethod
    def get_right_shoulder_button_down(cls) -> bool:
        return cls.get_button_down(sdl2.SDL_CONTROLLER_BUTTON_RIGHTSHOULDER)

    @classmethod
    def get_right_shoulder_button_up(cls) -> bool:
        return cls.get_button_up(sdl2.SDL_CONTROLLER_BUTTON_RIGHTSHOULDER)

    @classmethod
    def get_dpad_up_button(cls) -> bool:
        return cls.get_button(sdl2.SDL_CONTROLLER_BUTTON_DPAD_UP)

    @classmethod
    def get_dpad_up_button_down(cls) -> bool:
        return cls.get_button_down(sdl2.SDL_CONTROLLER_BUTTON_DPAD_UP)

    @classmethod
    def get_dpad_up_button_up(cls) -> bool:
        return cls.get_button_up(sdl2.SDL_CONTROLLER_BUTTON_DPAD_UP)

    @classmethod
    def get_dpad_down_button(cls) -> bool:
        return cls.get_button(sdl2.SDL_CONTROLLER_BUTTON_DPAD_DOWN)

    @classmethod
    def get_dpad_down_button_down(cls) -> bool:
        return cls.get_button_down(sdl2.SDL_CONTROLLER_BUTTON_DPAD_DOWN)

    @classmethod
    def get_dpad_down_button_up(cls) -> bool:
        return cls.get_button_up(sdl2.SDL_CONTROLLER_BUTTON_DPAD_DOWN)

    @classmethod
    def get_dpad_left_button(cls) -> bool:
        return cls.get_button(sdl2.SDL_CONTROLLER_BUTTON_DPAD_LEFT)

    @classmethod
    def get_dpad_left_button_down(cls) -> bool:
        return cls.get_button_down(sdl2.SDL_CONTROLLER_BUTTON_DPAD_LEFT)

    @classmethod
    def get_dpad_left_button_up(cls) -> bool:
        return cls.get_button_up(sdl2.SDL_CONTROLLER_BUTTON_DPAD_LEFT)

    @classmethod
    def get_dpad_right_button(cls) -> bool:
        return cls.get_button(sdl2.SDL_CONTROLLER_BUTTON_DPAD_RIGHT)

    @classmethod
    def get_dpad_right_button_down(cls) -> bool:
        return cls.get_button_down(sdl2.SDL_CONTROLLER_BUTTON_DPAD_RIGHT)

    @classmethod
    def get_dpad_right_button_up(cls) -> bool:
        return cls.get_button_up(sdl2.SDL_CONTROLLER_BUTTON_DPAD_RIGHT)

    @classmethod
    def get_misc1_button(cls) -> bool:
        return cls.get_button(sdl2.SDL_CONTROLLER_BUTTON_MISC1)

    @classmethod
    def get_misc1_button_down(cls) -> bool:
        return cls.get_button_down(sdl2.SDL_CONTROLLER_BUTTON_MISC1)

    @classmethod
    def get_misc1_button_up(cls) -> bool:
        return cls.get_button_up(sdl2.SDL_CONTROLLER_BUTTON_MISC1)

    @classmethod
    def get_paddle1_button(cls) -> bool:
        return cls.get_button(sdl2.SDL_CONTROLLER_BUTTON_PADDLE1)

    @classmethod
    def get_paddle1_button_down(cls) -> bool:
        return cls.get_button_down(sdl2.SDL_CONTROLLER_BUTTON_PADDLE1)

    @classmethod
    def get_paddle1_button_up(cls) -> bool:
        return cls.get_button_up(sdl2.SDL_CONTROLLER_BUTTON_PADDLE1)

    @classmethod
    def get_paddle2_button(cls) -> bool:
        return cls.get_button(sdl2.SDL_CONTROLLER_BUTTON_PADDLE2)

    @classmethod
    def get_paddle2_button_down(cls) -> bool:
        return cls.get_button_down(sdl2.SDL_CONTROLLER_BUTTON_PADDLE2)

    @classmethod
    def get_paddle2_button_up(cls) -> bool:
        return cls.get_button_up(sdl2.SDL_CONTROLLER_BUTTON_PADDLE2)

    @classmethod
    def get_paddle3_button(cls) -> bool:
        return cls.get_button(sdl2.SDL_CONTROLLER_BUTTON_PADDLE3)

    @classmethod
    def get_paddle3_button_down(cls) -> bool:
        return cls.get_button_down(sdl2.SDL_CONTROLLER_BUTTON_PADDLE3)

    @classmethod
    def get_paddle3_button_up(cls) -> bool:
        return cls.get_button_up(sdl2.SDL_CONTROLLER_BUTTON_PADDLE3)

    @classmethod
    def get_paddle4_button(cls) -> bool:
        return cls.get_button(sdl2.SDL_CONTROLLER_BUTTON_PADDLE4)

    @classmethod
    def get_paddle4_button_down(cls) -> bool:
        return cls.get_button_down(sdl2.SDL_CONTROLLER_BUTTON_PADDLE4)

    @classmethod
    def get_paddle4_button_up(cls) -> bool:
        return cls.get_button_up(sdl2.SDL_CONTROLLER_BUTTON_PADDLE4)

    @classmethod
    def get_touchpad_button(cls) -> bool:
        return cls.get_button(sdl2.SDL_CONTROLLER_BUTTON_TOUCHPAD)

    @classmethod
    def get_touchpad_button_down(cls) -> bool:
        return cls.get_button_down(sdl2.SDL_CONTROLLER_BUTTON_TOUCHPAD)

    @classmethod
    def get_touchpad_button_up(cls) -> bool:
        return cls.get_button_up(sdl2.SDL_CONTROLLER_BUTTON_TOUCHPAD)

    @classmethod
    def get_axis_left_x(cls, controller_id: int | None = None) -> float:
        """ Get the left analog stick's X axis value. """
        if controller := cls._get_controller(controller_id):
            return controller.get_axis_left_x()
        return 0

    @classmethod
    def get_axis_left_y(cls, controller_id: int | None = None) -> float:
        """ Get the left analog stick's Y axis value. """
        if controller := cls._get_controller(controller_id):
            return controller.get_axis_left_y()
        return 0

    @classmethod
    def get_axis_right_x(cls, controller_id: int | None = None) -> float:
        """ Get the right analog stick's X axis value. """
        if controller := cls._get_controller(controller_id):
            return controller.get_axis_right_x()
        return 0

    @classmethod
    def get_axis_right_y(cls, controller_id: int | None = None) -> float:
        """ Get the right analog stick's Y axis value. """
        if controller := cls._get_controller(controller_id):
            return controller.get_axis_right_y()
        return 0

    @classmethod
    def get_left_analog_stick(cls, controller_id: int | None = None) -> Vector2:
        """ Get the left analog stick's value. """
        if controller := cls._get_controller(controller_id):
            return controller.get_left_analog_stick()
        return Vector2.zero()

    @classmethod
    def get_right_analog_stick(cls, controller_id: int | None = None) -> Vector2:
        """ Get the right analog stick's value. """
        if controller := cls._get_controller(controller_id):
            return controller.get_right_analog_stick()
        return Vector2.zero()

    @classmethod
    def get_left_trigger(cls, controller_id: int | None = None) -> float:
        """ Get the left trigger's value. """
        if controller := cls._get_controller(controller_id):
            return controller.get_left_trigger()
        return 0

    @classmethod
    def get_right_trigger(cls, controller_id: int | None = None) -> float:
        """ Get the right trigger's value. """
        if controller := cls._get_controller(controller_id):
            return controller.get_right_trigger()
        return 0

    @staticmethod
    def _get_controller(controller_id: int | None = None) -> GameController | None:
        """ Get a controller from its joystick instance id.
        If no id is provided, the active controller will be returned.
        """
        if controller_id is None:
            controller_id = InputManager.get_active_controller_id()

        if controller_id is None:
            return None

        return InputManager.get_controller(controller_id)
