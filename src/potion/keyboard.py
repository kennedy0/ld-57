import sdl2

from potion.input_manager import InputManager


class Keyboard:
    """ Get information about the keyboard state. """
    @classmethod
    def get_key(cls, key: int) -> bool:
        """ Check if a key is pressed. """
        return InputManager.get_key(key)

    @classmethod
    def get_key_down(cls, key: int) -> bool:
        """ Check if a key was pressed this frame. """
        return InputManager.get_key_down(key)

    @classmethod
    def get_key_up(cls, key: int) -> bool:
        """ Check if a key was released this frame. """
        return InputManager.get_key_up(key)

    @classmethod
    def get_keys_pressed(cls) -> tuple[int]:
        """ Get a list of all keys that are currently pressed. """
        return InputManager.get_keys_pressed()

    @classmethod
    def get_key_names_pressed(cls) -> tuple[str]:
        """ Get a list of all key names that are currently pressed. """
        key_names = []

        for key in cls.get_keys_pressed():
            key_name = cls.key_to_name(key)
            if key_name:
                key_names.append(key_name)

        return tuple(key_names)

    @classmethod
    def key_code(cls, key_name: str) -> int:
        """ Get the key code from the name of a key. """
        return cls.name_to_key(key_name)

    @classmethod
    def get_shift(cls) -> bool:
        """ Check if Shift is held. """
        return cls.get_key(cls.LEFT_SHIFT) or cls.get_key(cls.RIGHT_SHIFT)

    @classmethod
    def get_ctrl(cls) -> bool:
        """ Check if Control is held. """
        return cls.get_key(cls.LEFT_CTRL) or cls.get_key(cls.RIGHT_CTRL)

    @classmethod
    def get_alt(cls) -> bool:
        """ Check if Alt is held. """
        return cls.get_key(cls.LEFT_ALT) or cls.get_key(cls.RIGHT_ALT)
    
    @staticmethod
    def key_to_name(key: int) -> str | None:
        """ Get the human-readable name for a key. """
        name = sdl2.SDL_GetKeyName(key)
        if isinstance(name, bytes):
            name = name.decode("utf-8")
            return name
    
    @staticmethod
    def name_to_key(name: str) -> int | None:
        """ Get the key code from its name. """
        key = sdl2.SDL_GetKeyFromName(name.encode("utf-8"))
        if key == sdl2.SDLK_UNKNOWN:
            return None
        else:
            return key

    A: int = name_to_key("a")
    B: int = name_to_key("b")
    C: int = name_to_key("c")
    D: int = name_to_key("d")
    E: int = name_to_key("e")
    F: int = name_to_key("f")
    G: int = name_to_key("g")
    H: int = name_to_key("h")
    I: int = name_to_key("i")
    J: int = name_to_key("j")
    K: int = name_to_key("k")
    L: int = name_to_key("l")
    M: int = name_to_key("m")
    N: int = name_to_key("n")
    O: int = name_to_key("o")
    P: int = name_to_key("p")
    Q: int = name_to_key("q")
    R: int = name_to_key("r")
    S: int = name_to_key("s")
    T: int = name_to_key("t")
    U: int = name_to_key("u")
    V: int = name_to_key("v")
    W: int = name_to_key("w")
    X: int = name_to_key("x")
    Y: int = name_to_key("y")
    Z: int = name_to_key("z")

    NUM_0: int = name_to_key("0")
    NUM_1: int = name_to_key("1")
    NUM_2: int = name_to_key("2")
    NUM_3: int = name_to_key("3")
    NUM_4: int = name_to_key("4")
    NUM_5: int = name_to_key("5")
    NUM_6: int = name_to_key("6")
    NUM_7: int = name_to_key("7")
    NUM_8: int = name_to_key("8")
    NUM_9: int = name_to_key("9")

    F1: int = name_to_key("F1")
    F2: int = name_to_key("F2")
    F3: int = name_to_key("F3")
    F4: int = name_to_key("F4")
    F5: int = name_to_key("F5")
    F6: int = name_to_key("F6")
    F7: int = name_to_key("F7")
    F8: int = name_to_key("F8")
    F9: int = name_to_key("F9")
    F10: int = name_to_key("F10")
    F11: int = name_to_key("F11")
    F12: int = name_to_key("F12")

    ESCAPE: int = name_to_key("Escape")

    BACKSPACE: int = name_to_key("Backspace")
    RETURN: int = name_to_key("Return")

    INSERT: int = name_to_key("Insert")
    DELETE: int = name_to_key("Delete")
    HOME: int = name_to_key("Home")
    END: int = name_to_key("End")
    PAGE_UP: int = name_to_key("PageUp")
    PAGE_DOWN: int = name_to_key("PageDown")

    TAB: int = name_to_key("Tab")
    SPACE: int = name_to_key("Space")

    LEFT_SHIFT: int = name_to_key("Left Shift")
    RIGHT_SHIFT: int = name_to_key("Right Shift")

    LEFT_CTRL: int = name_to_key("Left Ctrl")
    RIGHT_CTRL: int = name_to_key("Right Ctrl")

    LEFT_ALT: int = name_to_key("Left Alt")
    RIGHT_ALT: int = name_to_key("Right Alt")

    UP_ARROW: int = name_to_key("Up")
    DOWN_ARROW: int = name_to_key("Down")
    LEFT_ARROW: int = name_to_key("Left")
    RIGHT_ARROW: int = name_to_key("Right")

    KEYPAD_0: int = name_to_key("Keypad 0")
    KEYPAD_1: int = name_to_key("Keypad 1")
    KEYPAD_2: int = name_to_key("Keypad 2")
    KEYPAD_3: int = name_to_key("Keypad 3")
    KEYPAD_4: int = name_to_key("Keypad 4")
    KEYPAD_5: int = name_to_key("Keypad 5")
    KEYPAD_6: int = name_to_key("Keypad 6")
    KEYPAD_7: int = name_to_key("Keypad 7")
    KEYPAD_8: int = name_to_key("Keypad 8")
    KEYPAD_9: int = name_to_key("Keypad 9")
    KEYPAD_PERIOD: int = name_to_key("Keypad .")
    KEYPAD_ENTER: int = name_to_key("Keypad Enter")
    KEYPAD_PLUS: int = name_to_key("Keypad +")
    KEYPAD_MINUS: int = name_to_key("Keypad -")
