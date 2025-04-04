from __future__ import annotations

from ctypes import byref, c_int
from typing import TYPE_CHECKING

import sdl2

from potion.game_controller import GameController
from potion.log import Log

if TYPE_CHECKING:
    from potion.input_button import InputButton


class InputManager:
    """ Get keyboard, mouse, and controller input. """
    # The input system with the most recent activity
    __is_keyboard_active = True
    __is_mouse_active = False
    __is_controller_active = False

    __is_keyboard_set_active_this_frame = False
    __is_mouse_set_active_this_frame = False
    __is_controller_set_active_this_frame = False

    # Keys pressed
    __keys: set = set()
    __current_keys: set = set()
    __previous_keys: set = set()
    __key_repeats: set = set()

    # Text input
    __text: str = ""

    # Mouse buttons pressed
    __mouse_buttons: set = set()
    __current_mouse_buttons: set = set()
    __previous_mouse_buttons: set = set()

    # Mouse position
    __mouse_x: int = 0
    __mouse_y: int = 0
    __previous_mouse_x: int = 0
    __previous_mouse_y: int = 0

    # Mouse scroll wheel
    __mouse_scroll_wheel: int = 0

    # Mouse focus
    __is_mouse_in_window: bool = False

    # All connected game controllers
    # The key in the dictionary is the controller's joystick instance id
    __game_controllers: dict[int, GameController] = {}

    # The controller with the most recent input
    __active_controller_id: int | None = None

    # Input system for abstract buttons
    __input_buttons: dict[str, InputButton] = {}

    @classmethod
    def update(cls) -> None:
        """ Update the current input state. """
        # Update keyboard
        cls.__previous_keys = cls.__current_keys.copy()
        cls.__current_keys = cls.__keys.copy()
        cls.__is_keyboard_set_active_this_frame = False
        cls.__key_repeats.clear()
        cls.__text = ""

        # Update mouse
        cls.__previous_mouse_buttons = cls.__current_mouse_buttons.copy()
        cls.__current_mouse_buttons = cls.__mouse_buttons.copy()
        cls.__previous_mouse_x = cls.__mouse_x
        cls.__previous_mouse_y = cls.__mouse_y
        cls.__is_mouse_set_active_this_frame = False
        cls.__mouse_scroll_wheel = 0

        # Update mouse position
        mouse_x = c_int()
        mouse_y = c_int()
        sdl2.SDL_GetMouseState(byref(mouse_x), byref(mouse_y))
        cls.__mouse_x = mouse_x.value
        cls.__mouse_y = mouse_y.value
        if cls.__mouse_x != cls.__previous_mouse_x or cls.__mouse_y != cls.__previous_mouse_y:
            cls.set_mouse_active()

        # Update controllers
        cls.__is_controller_set_active_this_frame = False
        for controller in cls.__game_controllers.values():
            controller.update()

    @classmethod
    def is_keyboard_active(cls) -> bool:
        """ Check whether the keyboard is the device with the most recent input activity. """
        return cls.__is_keyboard_active

    @classmethod
    def is_keyboard_set_active_this_frame(cls) -> bool:
        """ Check if the keyboard became the device with the most recent input activity this frame. """
        return cls.__is_keyboard_set_active_this_frame

    @classmethod
    def is_mouse_active(cls) -> bool:
        """ Check whether the mouse is the device with the most recent input activity. """
        return cls.__is_mouse_active

    @classmethod
    def is_mouse_set_active_this_frame(cls) -> bool:
        """ Check if the mouse became the device with the most recent input activity this frame. """
        return cls.__is_mouse_set_active_this_frame

    @classmethod
    def is_mouse_in_window(cls) -> bool:
        """ Check if the mouse is inside the window. """
        return cls.__is_mouse_in_window

    @classmethod
    def is_keyboard_mouse_active(cls) -> bool:
        """ Check whether the keyboard or mouse are the devices with the most recent input activity. """
        return cls.__is_keyboard_active or cls.__is_mouse_active

    @classmethod
    def is_controller_active(cls) -> bool:
        """ Check whether a controller is device with the most recent input activity. """
        return cls.__is_controller_active

    @classmethod
    def is_controller_set_active_this_frame(cls) -> bool:
        """ Check if a controller became the device with the most recent input activity this frame. """
        return cls.__is_controller_set_active_this_frame

    @classmethod
    def set_keyboard_active(cls) -> None:
        """ Indicate that the keyboard is the device with the most recent input activity. """
        if not cls.__is_keyboard_active:
            cls.__is_keyboard_set_active_this_frame = True

        cls.__is_keyboard_active = True
        cls.__is_mouse_active = False
        cls.__is_controller_active = False

    @classmethod
    def set_mouse_active(cls) -> None:
        """ Indicate that the mouse is the device with the most recent input activity. """
        if not cls.__is_mouse_active:
            cls.__is_mouse_set_active_this_frame = True

        cls.__is_keyboard_active = False
        cls.__is_mouse_active = True
        cls.__is_controller_active = False

    @classmethod
    def set_controller_active(cls) -> None:
        """ Indicate that a controller is the device with the most recent input activity. """
        if not cls.__is_controller_active:
            cls.__is_controller_set_active_this_frame = True

        cls.__is_keyboard_active = False
        cls.__is_mouse_active = False
        cls.__is_controller_active = True

    @classmethod
    def register_key_down(cls, key: int) -> None:
        """ Indicate that a key on the keyboard has been pressed. """
        cls.__keys.add(key)
        cls.set_keyboard_active()

    @classmethod
    def register_key_up(cls, key: int) -> None:
        """ Indicate that a key on the keyboard has been released. """
        cls.__keys.remove(key)

    @classmethod
    def register_key_repeat(cls, key: int) -> None:
        """ Indicate that a key on the keyboard has been held and triggered a repeat event. """
        cls.__key_repeats.add(key)
        cls.set_keyboard_active()

    @classmethod
    def register_text_input(cls, text: str) -> None:
        """ Indicate that text input has been received. """
        cls.__text += text
        cls.set_keyboard_active()

    @classmethod
    def register_mouse_enter_window(cls) -> None:
        """ Indicate that the mouse entered the window. """
        cls.__is_mouse_in_window = True

    @classmethod
    def register_mouse_leave_window(cls) -> None:
        """ Indicate that the mouse left the window. """
        cls.__is_mouse_in_window = False

    @classmethod
    def register_mouse_down(cls, mouse_button: int) -> None:
        """ Indicate that a mouse button has been pressed. """
        cls.__mouse_buttons.add(mouse_button)
        cls.set_mouse_active()

    @classmethod
    def register_mouse_up(cls, mouse_button: int) -> None:
        """ Indicate that a mouse button has been released. """
        cls.__mouse_buttons.remove(mouse_button)

    @classmethod
    def register_mouse_scroll_wheel(cls, scroll: int) -> None:
        """ Indicate that the mouse wheel has been scrolled up or down. """
        cls.__mouse_scroll_wheel = scroll
        cls.set_mouse_active()

    @classmethod
    def register_controller_added(cls, device_index: int) -> None:
        """ Indicate that a game controller has been added. """
        game_controller = GameController(device_index)
        cls.__game_controllers[game_controller.joystick_instance_id] = game_controller
        cls.__active_controller_id = game_controller.joystick_instance_id
        cls.set_controller_active()

    @classmethod
    def register_controller_removed(cls, controller_id: int) -> None:
        """ Indicate that a game controller has been removed. """
        if cls.__active_controller_id == controller_id:
            cls.__active_controller_id = None
        cls.__game_controllers[controller_id].close()
        del cls.__game_controllers[controller_id]

    @classmethod
    def register_controller_button_down(cls, controller_id: int, button: int) -> None:
        """ Indicate that a button on the controller has been pressed. """
        cls.__game_controllers[controller_id].register_button_down(button)
        cls.__active_controller_id = controller_id
        cls.set_controller_active()

    @classmethod
    def register_controller_button_up(cls, controller_id: int, button: int) -> None:
        """ Indicate that a button on the controller has been released. """
        cls.__game_controllers[controller_id].register_button_up(button)

    @classmethod
    def register_controller_axis_motion(cls, controller_id: int, axis: int, value: int) -> None:
        """ Indicate that an axis value on a controller has changed. """
        cls.__game_controllers[controller_id].register_axis_motion(axis, value)

    @classmethod
    def get_key(cls, key: int) -> bool:
        """ Check if a key is pressed. """
        return key in cls.__current_keys

    @classmethod
    def get_key_down(cls, key: int) -> bool:
        """ Check if a key was pressed this frame. """
        return key in cls.__current_keys and key not in cls.__previous_keys

    @classmethod
    def get_key_up(cls, key: int) -> bool:
        """ Check if a key was released this frame. """
        return key not in cls.__current_keys and key in cls.__previous_keys

    @classmethod
    def get_keys_pressed(cls) -> tuple[int]:
        """ Get a list of all keys that are currently pressed. """
        return tuple(cls.__current_keys)

    @classmethod
    def get_key_repeat(cls, key: int) -> bool:
        """ Check if a key was held and repeated this frame. """
        return key in cls.__key_repeats

    @classmethod
    def get_text_input(cls) -> str:
        """ Get the text input received this frame. """
        return cls.__text

    @classmethod
    def get_mouse(cls, mouse_button: int) -> bool:
        """ Check if a mouse button is pressed. """
        return mouse_button in cls.__current_mouse_buttons

    @classmethod
    def get_mouse_down(cls, mouse_button: int) -> bool:
        """ Check if a mouse button was pressed this frame. """
        return mouse_button in cls.__current_mouse_buttons and mouse_button not in cls.__previous_mouse_buttons

    @classmethod
    def get_mouse_up(cls, mouse_button: int) -> bool:
        """ Check if a mouse button was released this frame. """
        return mouse_button not in cls.__current_mouse_buttons and mouse_button in cls.__previous_mouse_buttons

    @classmethod
    def get_left_mouse(cls) -> bool:
        """ Check if the left mouse button is pressed. """
        return cls.get_mouse(sdl2.SDL_BUTTON_LEFT)

    @classmethod
    def get_left_mouse_down(cls) -> bool:
        """ Check if the left mouse button was pressed this frame. """
        return cls.get_mouse_down(sdl2.SDL_BUTTON_LEFT)

    @classmethod
    def get_left_mouse_up(cls) -> bool:
        """ Check if the left mouse button was released this frame. """
        return cls.get_mouse_up(sdl2.SDL_BUTTON_LEFT)

    @classmethod
    def get_right_mouse(cls) -> bool:
        """ Check if the right mouse button is pressed. """
        return cls.get_mouse(sdl2.SDL_BUTTON_RIGHT)

    @classmethod
    def get_right_mouse_down(cls) -> bool:
        """ Check if the right mouse button was pressed this frame. """
        return cls.get_mouse_down(sdl2.SDL_BUTTON_RIGHT)

    @classmethod
    def get_right_mouse_up(cls) -> bool:
        """ Check if the right mouse button was released this frame. """
        return cls.get_mouse_up(sdl2.SDL_BUTTON_RIGHT)

    @classmethod
    def get_middle_mouse(cls) -> bool:
        """ Check if the middle mouse button is pressed. """
        return cls.get_mouse(sdl2.SDL_BUTTON_MIDDLE)

    @classmethod
    def get_middle_mouse_down(cls) -> bool:
        """ Check if the middle mouse button was pressed this frame. """
        return cls.get_mouse_down(sdl2.SDL_BUTTON_MIDDLE)

    @classmethod
    def get_middle_mouse_up(cls) -> bool:
        """ Check if the middle mouse button was released this frame. """
        return cls.get_mouse_up(sdl2.SDL_BUTTON_MIDDLE)

    @classmethod
    def get_mouse_x(cls) -> int:
        """ Get the X position of the mouse cursor. """
        return cls.__mouse_x

    @classmethod
    def get_mouse_y(cls) -> int:
        """ Get the Y position of the mouse cursor. """
        return cls.__mouse_y

    @classmethod
    def get_mouse_move_x(cls) -> int:
        """ Get the mouse movement on the X axis this frame. """
        return cls.__mouse_x - cls.__previous_mouse_x

    @classmethod
    def get_mouse_move_y(cls) -> int:
        """ Get the mouse movement on the Y axis this frame. """
        return cls.__mouse_y - cls.__previous_mouse_y

    @classmethod
    def get_mouse_scroll_wheel(cls) -> int:
        """ Get the mouse scroll wheel movement this frame. """
        return cls.__mouse_scroll_wheel

    @classmethod
    def get_all_controllers(cls) -> tuple[GameController]:
        """ Get a list of all game controllers. """
        return tuple(cls.__game_controllers.values())

    @classmethod
    def get_active_controller_id(cls) -> int | None:
        """ Get the instance id of the controller with the most recent input. """
        return cls.__active_controller_id

    @classmethod
    def get_controller(cls, controller_id: int) -> GameController | None:
        """ Get a controller from its instance id. """
        return cls.__game_controllers.get(controller_id)

    @classmethod
    def get_active_controller(cls) -> GameController | None:
        """ Get the controller with the most recent input. """
        return cls.get_controller(cls.get_active_controller_id())

    @classmethod
    def get_controller_button(cls, controller_id: int, button: int) -> bool:
        """ Check if a button on a controller is pressed. """
        return cls.__game_controllers[controller_id].get_button(button)

    @classmethod
    def get_controller_button_down(cls, controller_id: int, button: int) -> bool:
        """ Check if a button on a controller was pressed this frame. """
        return cls.__game_controllers[controller_id].get_button_down(button)

    @classmethod
    def get_controller_button_up(cls, controller_id: int, button: int) -> bool:
        """ Check if a button on a controller was released this frame. """
        return cls.__game_controllers[controller_id].get_button_up(button)

    @classmethod
    def get_controller_axis(cls, controller_id: int, axis: int) -> float:
        """ Get the current value from an axis. """
        return cls.__game_controllers[controller_id].get_axis(axis)

    @classmethod
    def get_controller_digital_axis(cls, controller_id: int, axis: int, direction: int) -> bool:
        """ Check if the digital representation of an axis direction is pressed.
        'direction' determines whether the positive or negative axis direction is used, and should be either -1 or 1.
        """
        return cls.__game_controllers[controller_id].get_digital_axis(axis, direction)

    @classmethod
    def get_controller_digital_axis_down(cls, controller_id: int, axis: int, direction: int) -> bool:
        """ Check if the digital representation of an axis direction was pressed this frame.
        'direction' determines whether the positive or negative axis direction is used, and should be either -1 or 1.
        """
        return cls.__game_controllers[controller_id].get_digital_axis_down(axis, direction)

    @classmethod
    def get_controller_digital_axis_up(cls, controller_id: int, axis: int, direction: int) -> bool:
        """ Check if the digital representation of an axis direction was released this frame.
        'direction' determines whether the positive or negative axis direction is used, and should be either -1 or 1.
        """
        return cls.__game_controllers[controller_id].get_digital_axis_up(axis, direction)

    @classmethod
    def add_input_button(cls, button: InputButton) -> None:
        """ Add a new button for the Input system. """
        cls.__input_buttons[button.name] = button

    @classmethod
    def map_key_to_input_button(cls, key: int | None, button_name: str) -> None:
        """ Map a key on the keyboard to an Input button. """
        cls.__input_buttons[button_name].key = key

    @classmethod
    def map_mouse_button_to_input_button(cls, mouse_button: int | None, button_name: str) -> None:
        """ Map a mouse button to an Input button. """
        cls.__input_buttons[button_name].mouse_button = mouse_button

    @classmethod
    def map_controller_button_to_input_button(cls, controller_button: int | None, button_name: str) -> None:
        """ Map a controller button to an Input button. """
        cls.__input_buttons[button_name].controller_button = controller_button

    @classmethod
    def map_controller_axis_to_input_button(cls, axis: int | None, direction: int, button_name: str) -> None:
        """ Map a controller button to an Input button.
        'direction' determines whether the positive or negative axis direction is used, and should be either -1 or 1.
        """
        cls.__input_buttons[button_name].controller_axis = axis
        if direction < 0:
            cls.__input_buttons[button_name].set_controller_axis_negative()
        else:
            cls.__input_buttons[button_name].set_controller_axis_positive()

    @classmethod
    def get_input_button(cls, button_name: str) -> bool:
        """ Check if a button for the Input system is pressed. """
        try:
            return cls.__input_buttons[button_name].get_button()
        except KeyError:
            Log.error(f"No input button named {button_name}")
            return False

    @classmethod
    def get_input_button_down(cls, button_name: str) -> bool:
        """ Check if a button for the Input system was pressed this frame. """
        try:
            return cls.__input_buttons[button_name].get_button_down()
        except KeyError:
            Log.error(f"No input button named {button_name}")
            return False

    @classmethod
    def get_input_button_up(cls, button_name: str) -> bool:
        """ Check if a button for the Input system was released this frame. """
        try:
            return cls.__input_buttons[button_name].get_button_up()
        except KeyError:
            Log.error(f"No input button named {button_name}")
            return False
