import sdl2

from potion.keyboard import Keyboard
from potion.input_button import InputButton
from potion.input_manager import InputManager


class Input:
    """ The Input system abstracts input from devices into virtual buttons.

    This makes it possible to assign different, or multiple, inputs into the same action.

    In general, game logic should look for input from here, rather than directly using Keyboard, mouse, or controller.
    """
    @classmethod
    def add_button(cls, button_name: str) -> None:
        """ Add a button. """
        button = InputButton(button_name)
        InputManager.add_input_button(button)

    @classmethod
    def map_key_to_button(cls, key: int, button_name: str) -> None:
        """ Map a key on the keyboard to a button. """
        InputManager.map_key_to_input_button(key, button_name)

    @classmethod
    def clear_key_assignment_for_button(cls, button_name: str) -> None:
        """ Remove the key assignment for a button. """
        InputManager.map_key_to_input_button(None, button_name)

    @classmethod
    def map_mouse_button_to_button(cls, mouse_button: int, button_name: str) -> None:
        """ Map a mouse button to a button. """
        InputManager.map_mouse_button_to_input_button(mouse_button, button_name)

    @classmethod
    def clear_mouse_button_assignment_for_button(cls, button_name: str) -> None:
        """ Remove the mouse button assignment for a button. """
        InputManager.map_mouse_button_to_input_button(None, button_name)

    @classmethod
    def map_controller_button_to_button(cls, controller_button: int, button_name: str) -> None:
        """ Map a controller button to a button. """
        InputManager.map_controller_button_to_input_button(controller_button, button_name)

    @classmethod
    def clear_controller_button_assignment_for_button(cls, button_name: str) -> None:
        """ Remove the controller button assignment for a button. """
        InputManager.map_controller_button_to_input_button(None, button_name)

    @classmethod
    def map_controller_axis_to_button(cls, controller_button: int, direction: int, button_name: str) -> None:
        """ Map a controller axis to a button.
        'direction' determines whether the positive or negative axis direction is used, and should be either -1 or 1.
        """
        InputManager.map_controller_axis_to_input_button(controller_button, direction, button_name)

    @classmethod
    def clear_controller_axis_assignment_for_button(cls, button_name: str) -> None:
        """ Remove the controller axis assignment for a button. """
        InputManager.map_controller_axis_to_input_button(None, 1, button_name)

    @classmethod
    def get_button(cls, button_name: str) -> bool:
        """ Check if a button is pressed. """
        return InputManager.get_input_button(button_name)

    @classmethod
    def get_button_down(cls, button_name: str) -> bool:
        """ Check if a button was pressed this frame. """
        return InputManager.get_input_button_down(button_name)

    @classmethod
    def get_button_up(cls, button_name: str) -> bool:
        """ Check if a button was released this frame. """
        return InputManager.get_input_button_up(button_name)

    @classmethod
    def init_default(cls) -> None:
        """ Initialize a set of default inputs that is good enough for quick demos. """
        cls.add_button("Confirm")
        cls.map_key_to_button(Keyboard.RETURN, "Confirm")
        cls.map_controller_button_to_button(sdl2.SDL_CONTROLLER_BUTTON_A, "Confirm")

        cls.add_button("Cancel")
        cls.map_key_to_button(Keyboard.BACKSPACE, "Cancel")
        cls.map_controller_button_to_button(sdl2.SDL_CONTROLLER_BUTTON_B, "Cancel")

        cls.add_button("Up")
        cls.map_key_to_button(Keyboard.UP_ARROW, "Up")
        cls.map_controller_button_to_button(sdl2.SDL_CONTROLLER_BUTTON_DPAD_UP, "Up")
        cls.map_controller_axis_to_button(sdl2.SDL_CONTROLLER_AXIS_LEFTY, -1, "Up")

        cls.add_button("Down")
        cls.map_key_to_button(Keyboard.DOWN_ARROW, "Down")
        cls.map_controller_button_to_button(sdl2.SDL_CONTROLLER_BUTTON_DPAD_DOWN, "Down")
        cls.map_controller_axis_to_button(sdl2.SDL_CONTROLLER_AXIS_LEFTY, 1, "Down")

        cls.add_button("Left")
        cls.map_key_to_button(Keyboard.LEFT_ARROW, "Left")
        cls.map_controller_button_to_button(sdl2.SDL_CONTROLLER_BUTTON_DPAD_LEFT, "Left")
        cls.map_controller_axis_to_button(sdl2.SDL_CONTROLLER_AXIS_LEFTX, -1, "Left")

        cls.add_button("Right")
        cls.map_key_to_button(Keyboard.RIGHT_ARROW, "Right")
        cls.map_controller_button_to_button(sdl2.SDL_CONTROLLER_BUTTON_DPAD_RIGHT, "Right")
        cls.map_controller_axis_to_button(sdl2.SDL_CONTROLLER_AXIS_LEFTX, 1, "Right")

        cls.add_button("Start")
        cls.map_key_to_button(Keyboard.ESCAPE, "Start")
        cls.map_controller_button_to_button(sdl2.SDL_CONTROLLER_BUTTON_START, "Start")
