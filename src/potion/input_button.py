from potion.input_manager import InputManager


class InputButton:
    """ An abstract button for the input system. """
    def __init__(self, name: str) -> None:
        self._name = name
        self._key = None
        self._mouse_button = None
        self._controller_button = None
        self._controller_axis = None
        self._controller_axis_direction = 1

    def __str__(self) -> str:
        return f"InputButton({self.name})"

    def __repr__(self) -> str:
        return str(self)

    @property
    def name(self) -> str:
        """ The button name. """
        return self._name

    @property
    def key(self) -> int | None:
        """ The key on the keyboard that is mapped to this button. """
        return self._key

    @key.setter
    def key(self, value: int | None) -> None:
        """ Set the key on the keyboard that is mapped to this button.
        Setting this value to None will clear the mapping.
        """
        self._key = value

    @property
    def mouse_button(self) -> int | None:
        """ The button on the mouse that is mapped to this button. """
        return self._mouse_button

    @mouse_button.setter
    def mouse_button(self, value: int | None) -> None:
        """ Set the button on the mouse that is mapped to this button.
        Setting this value to None will clear the mapping.
        """
        self._mouse_button = value

    @property
    def controller_button(self) -> int | None:
        """ The button on the controller that is mapped to this button. """
        return self._controller_button

    @controller_button.setter
    def controller_button(self, value: int | None) -> None:
        """ Set the button on the controller that is mapped to this button.
        Setting this value to None will clear the mapping.
        """
        self._controller_button = value

    @property
    def controller_axis(self) -> int | None:
        """ The axis on the controller that is mapped to this button. """
        return self._controller_axis

    @controller_axis.setter
    def controller_axis(self, value: int | None) -> None:
        """ Set the axis on the controller that is mapped to this button.
        Setting this value to None will clear the mapping.
        """
        self._controller_axis = value

    @property
    def controller_axis_direction(self) -> int:
        """ The direction of the controller axis that is mapped to this button.
        1 indicates a positive direction, -1 indicates a negative direction.
        """
        return self._controller_axis_direction

    def set_controller_axis_positive(self) -> None:
        """ Set the controller axis direction to be positive. """
        self._controller_axis_direction = 1

    def set_controller_axis_negative(self) -> None:
        """ Set the controller axis direction to be negative. """
        self._controller_axis_direction = -1

    def get_button(self) -> bool:
        """ Check if the button is pressed. """
        if button_key := self._get_button_from_key():
            return button_key
        elif button_mouse := self._get_button_from_mouse_button():
            return button_mouse
        elif button_controller := self._get_button_from_controller_button():
            return button_controller
        elif button_controller_axis := self._get_button_from_controller_digital_axis():
            return button_controller_axis
        else:
            return False

    def _get_button_from_key(self) -> bool:
        """ Check if the key for this button is pressed. """
        if self.key is not None:
            return InputManager.get_key(self.key)

        return False

    def _get_button_from_mouse_button(self) -> bool:
        """ Check if the mouse button for this button is pressed. """
        if self.mouse_button is not None:
            return InputManager.get_mouse(self.mouse_button)

        return False

    def _get_button_from_controller_button(self) -> bool:
        """ Check if the controller button for this button is pressed. """
        if self.controller_button is not None:
            controller_id = InputManager.get_active_controller_id()
            if controller_id is not None:
                return InputManager.get_controller_button(controller_id, self.controller_button)

        return False

    def _get_button_from_controller_digital_axis(self) -> bool:
        """ Check if the controller digital axis for this button is pressed. """
        if self.controller_axis is not None:
            controller_id = InputManager.get_active_controller_id()
            if controller_id is not None:
                return InputManager.get_controller_digital_axis(
                    controller_id,
                    self.controller_axis,
                    self.controller_axis_direction)

        return False

    def get_button_down(self) -> bool:
        """ Check if the button was pressed this frame. """
        if button_key_down := self._get_button_down_from_key_down():
            return button_key_down
        elif button_mouse_down := self._get_button_down_from_mouse_button_down():
            return button_mouse_down
        elif button_controller_down := self._get_button_down_from_controller_button_down():
            return button_controller_down
        elif button_controller_axis_down := self._get_button_down_from_controller_digital_axis_down():
            return button_controller_axis_down
        else:
            return False

    def _get_button_down_from_key_down(self) -> bool:
        """ Check if the key for this button was pressed this frame. """
        if self.key is not None:
            return InputManager.get_key_down(self.key)

        return False

    def _get_button_down_from_mouse_button_down(self) -> bool:
        """ Check if the mouse button for this button was pressed this frame. """
        if self.mouse_button is not None:
            return InputManager.get_mouse_down(self.mouse_button)

        return False

    def _get_button_down_from_controller_button_down(self) -> bool:
        """ Check if the controller button for this button was pressed this frame. """
        if self.controller_button is not None:
            controller_id = InputManager.get_active_controller_id()
            if controller_id is not None:
                return InputManager.get_controller_button_down(controller_id, self.controller_button)

        return False

    def _get_button_down_from_controller_digital_axis_down(self) -> bool:
        """ Check if the controller digital axis for this button is pressed. """
        if self.controller_axis is not None:
            controller_id = InputManager.get_active_controller_id()
            if controller_id is not None:
                return InputManager.get_controller_digital_axis_down(
                    controller_id,
                    self.controller_axis,
                    self.controller_axis_direction)

        return False

    def get_button_up(self) -> bool:
        """ Check if the button was released this frame. """
        if button_key_up := self._get_button_up_from_key_up():
            return button_key_up
        elif button_mouse_up := self._get_button_up_from_mouse_button_up():
            return button_mouse_up
        elif button_controller_up := self._get_button_up_from_controller_button_up():
            return button_controller_up
        elif button_controller_axis_up := self._get_button_up_from_controller_digital_axis_up():
            return button_controller_axis_up
        else:
            return False

    def _get_button_up_from_key_up(self) -> bool:
        """ Check if the key for this button was released this frame. """
        if self.key is not None:
            return InputManager.get_key_up(self.key)

        return False

    def _get_button_up_from_mouse_button_up(self) -> bool:
        """ Check if the mouse button for this button was released this frame. """
        if self.mouse_button is not None:
            return InputManager.get_mouse_up(self.mouse_button)

        return False

    def _get_button_up_from_controller_button_up(self) -> bool:
        """ Check if the controller button for this button was released this frame. """
        if self.controller_button is not None:
            controller_id = InputManager.get_active_controller_id()
            if controller_id is not None:
                return InputManager.get_controller_button_up(controller_id, self.controller_button)

        return False

    def _get_button_up_from_controller_digital_axis_up(self) -> bool:
        """ Check if the controller digital axis for this button is pressed. """
        if self.controller_axis is not None:
            controller_id = InputManager.get_active_controller_id()
            if controller_id is not None:
                return InputManager.get_controller_digital_axis_up(
                    controller_id,
                    self.controller_axis,
                    self.controller_axis_direction)

        return False
