from __future__ import annotations

from ctypes import POINTER
from typing import TYPE_CHECKING

import sdl2

from potion.content import Content
from potion.data_types.point import Point
from potion.input_manager import InputManager
from potion.log import Log
from potion.window import Window


if TYPE_CHECKING:
    from potion.camera import Camera


class Mouse:
    """ Get information about the mouse state. """

    # Creating before the Window is ready
    # The cursor constants are not initialized until the first time they're used.
    _CURSOR_ARROW = None
    _CURSOR_I_BEAM = None
    _CURSOR_WAIT = None
    _CURSOR_WAITARROW = None
    _CURSOR_CROSSHAIR = None
    _CURSOR_SIZENWSE = None
    _CURSOR_SIZENESW = None
    _CURSOR_SIZEWE = None
    _CURSOR_SIZENS = None
    _CURSOR_SIZEALL = None
    _CURSOR_NO = None
    _CURSOR_HAND = None

    _CUSTOM: dict[str, POINTER(sdl2.SDL_Cursor)] = {}

    # noinspection DuplicatedCode
    @classmethod
    def init_cursors(cls) -> None:
        """ Initialize cursors.
        This must be done after the Window is created.
        """
        cls._CURSOR_ARROW = sdl2.SDL_CreateSystemCursor(sdl2.SDL_SYSTEM_CURSOR_ARROW)
        cls._CURSOR_I_BEAM = sdl2.SDL_CreateSystemCursor(sdl2.SDL_SYSTEM_CURSOR_IBEAM)
        cls._CURSOR_WAIT = sdl2.SDL_CreateSystemCursor(sdl2.SDL_SYSTEM_CURSOR_WAIT)
        cls._CURSOR_WAITARROW = sdl2.SDL_CreateSystemCursor(sdl2.SDL_SYSTEM_CURSOR_WAITARROW)
        cls._CURSOR_CROSSHAIR = sdl2.SDL_CreateSystemCursor(sdl2.SDL_SYSTEM_CURSOR_CROSSHAIR)
        cls._CURSOR_SIZENWSE = sdl2.SDL_CreateSystemCursor(sdl2.SDL_SYSTEM_CURSOR_SIZENWSE)
        cls._CURSOR_SIZENESW = sdl2.SDL_CreateSystemCursor(sdl2.SDL_SYSTEM_CURSOR_SIZENESW)
        cls._CURSOR_SIZEWE = sdl2.SDL_CreateSystemCursor(sdl2.SDL_SYSTEM_CURSOR_SIZEWE)
        cls._CURSOR_SIZENS = sdl2.SDL_CreateSystemCursor(sdl2.SDL_SYSTEM_CURSOR_SIZENS)
        cls._CURSOR_SIZEALL = sdl2.SDL_CreateSystemCursor(sdl2.SDL_SYSTEM_CURSOR_SIZEALL)
        cls._CURSOR_NO = sdl2.SDL_CreateSystemCursor(sdl2.SDL_SYSTEM_CURSOR_NO)
        cls._CURSOR_HAND = sdl2.SDL_CreateSystemCursor(sdl2.SDL_SYSTEM_CURSOR_HAND)

    @classmethod
    def in_viewport(cls) -> bool:
        """ Check if the mouse is in the viewport. """
        if InputManager.is_mouse_in_window():
            if Window.viewport().contains_point(cls.screen_position()):
                return True

        return False

    @classmethod
    def screen_position(cls) -> Point:
        """ Get the screen position of the mouse cursor. """
        return Point(InputManager.get_mouse_x(), InputManager.get_mouse_y())

    @classmethod
    def world_position(cls, camera: Camera | None = None) -> Point:
        """ Get the world position of the mouse cursor.
        This has to be relative to a camera. If no camera is provided, the current scene's main camera will be implied.
        """
        if not camera:
            from potion.engine import Engine
            camera = Engine.scene().main_camera
        return camera.screen_to_world_position(cls.screen_position())

    @classmethod
    def get_left_mouse(cls) -> bool:
        """ Check if the left mouse button is pressed. """
        return InputManager.get_left_mouse()

    @classmethod
    def get_right_mouse(cls) -> bool:
        """ Check if the right mouse button is pressed. """
        return InputManager.get_right_mouse()

    @classmethod
    def get_middle_mouse(cls) -> bool:
        """ Check if the middle mouse button is pressed. """
        return InputManager.get_middle_mouse()

    @classmethod
    def get_left_mouse_down(cls) -> bool:
        """ Check if the left mouse button was pressed this frame. """
        return InputManager.get_left_mouse_down()

    @classmethod
    def get_left_mouse_up(cls) -> bool:
        """ Check if the left mouse button was released this frame. """
        return InputManager.get_left_mouse_up()

    @classmethod
    def get_right_mouse_down(cls) -> bool:
        """ Check if the right mouse button was pressed this frame. """
        return InputManager.get_right_mouse_down()

    @classmethod
    def get_right_mouse_up(cls) -> bool:
        """ Check if the right mouse button was released this frame. """
        return InputManager.get_right_mouse_up()

    @classmethod
    def get_middle_mouse_down(cls) -> bool:
        """ Check if the middle mouse button was pressed this frame. """
        return InputManager.get_middle_mouse_down()

    @classmethod
    def get_middle_mouse_up(cls) -> bool:
        """ Check if the middle mouse button was released this frame. """
        return InputManager.get_middle_mouse_up()

    @classmethod
    def get_mouse_scroll_wheel(cls) -> int:
        """ Get the mouse scroll wheel value this frame. """
        return InputManager.get_mouse_scroll_wheel()

    @classmethod
    def show_cursor(cls) -> None:
        """ Show the cursor. """
        sdl2.SDL_ShowCursor(sdl2.SDL_ENABLE)

    @classmethod
    def hide_cursor(cls) -> None:
        """ Hide the cursor. """
        sdl2.SDL_ShowCursor(sdl2.SDL_DISABLE)

    @classmethod
    def set_cursor_arrow(cls) -> None:
        """ Set the cursor to an arrow. """
        sdl2.SDL_SetCursor(cls._CURSOR_ARROW)

    @classmethod
    def set_cursor_text_select(cls) -> None:
        """ Set the cursor to an I-Beam for text selection. """
        sdl2.SDL_SetCursor(cls._CURSOR_I_BEAM)

    @classmethod
    def set_cursor_wait(cls) -> None:
        """ Set the cursor to an hourglass. """
        sdl2.SDL_SetCursor(cls._CURSOR_WAIT)

    @classmethod
    def set_cursor_wait_arrow(cls) -> None:
        """ Set the cursor to an arrow with a small hourglass. """
        sdl2.SDL_SetCursor(cls._CURSOR_WAITARROW)

    @classmethod
    def set_cursor_crosshair(cls) -> None:
        """ Set the cursor to a crosshair. """
        sdl2.SDL_SetCursor(cls._CURSOR_CROSSHAIR)

    @classmethod
    def set_cursor_resize_diagonal_down(cls) -> None:
        """ Set the cursor to a double-ended arrow pointing northwest and southeast. """
        sdl2.SDL_SetCursor(cls._CURSOR_SIZENWSE)

    @classmethod
    def set_cursor_resize_diagonal_up(cls) -> None:
        """ Set the cursor to a double-ended arrow pointing northeast and southwest. """
        sdl2.SDL_SetCursor(cls._CURSOR_SIZENESW)

    @classmethod
    def set_cursor_resize_horizontal(cls) -> None:
        """ Set the cursor to a double-ended arrow pointing west and east. """
        sdl2.SDL_SetCursor(cls._CURSOR_SIZEWE)

    @classmethod
    def set_cursor_resize_vertical(cls) -> None:
        """ Set the cursor to a double-ended arrow pointing north and south. """
        sdl2.SDL_SetCursor(cls._CURSOR_SIZENS)

    @classmethod
    def set_cursor_resize_all(cls) -> None:
        """ Set the cursor to a four-pointed arrow pointing north, south, east, and west. """
        sdl2.SDL_SetCursor(cls._CURSOR_SIZEALL)

    @classmethod
    def set_cursor_no(cls) -> None:
        """ Set the cursor to a slashed circle. """
        sdl2.SDL_SetCursor(cls._CURSOR_NO)

    @classmethod
    def set_cursor_hand(cls) -> None:
        """ Set the cursor to a hand. """
        sdl2.SDL_SetCursor(cls._CURSOR_HAND)

    @classmethod
    def create_custom_cursor(cls, content_path: str, cursor_name: str) -> None:
        """ Create a custom cursor.
        `content_path` is the path to the cursor image.
        """
        if cursor_name in cls._CUSTOM:
            Log.error(f"A custom cursor named '{cursor_name}' has already been created.")
            return

        # Create cursor
        texture = Content.load_texture(content_path)
        surface = texture.to_surface()
        cursor = sdl2.SDL_CreateColorCursor(surface, 0, 0)
        sdl2.SDL_FreeSurface(surface)

        # Add cursor to dict
        cls._CUSTOM[cursor_name] = cursor

    @classmethod
    def set_custom_cursor(cls, cursor_name: str) -> None:
        """ Set the cursor to a custom cursor. """
        if cursor_name not in cls._CUSTOM:
            Log.error(f"There is no custom cursor named '{cursor_name}'")
            return

        sdl2.SDL_SetCursor(cls._CUSTOM[cursor_name])
