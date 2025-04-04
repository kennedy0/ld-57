from __future__ import annotations

import ctypes

import sdl2

from potion.input_manager import InputManager
from potion.renderer import Renderer
from potion.window import Window


class EventManager:
    """ The event manager processes SDL events at the beginning of each update loop. """
    @staticmethod
    def process_events():
        """ Process all SDL events. """
        event = sdl2.SDL_Event()
        while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
            EventManager._handle_event(event)

    @staticmethod
    def _handle_event(event: sdl2.SDL_Event) -> None:
        """ Handle a single event. """
        match event.type:
            case sdl2.SDL_QUIT:
                EventManager._quit_event()
            case sdl2.SDL_WINDOWEVENT:
                EventManager._window_event(event)
            case sdl2.SDL_KEYDOWN | sdl2.SDL_KEYUP:
                EventManager._keyboard_event(event)
            case sdl2.SDL_TEXTINPUT:
                EventManager._text_input_event(event)
            case sdl2.SDL_MOUSEBUTTONDOWN | sdl2.SDL_MOUSEBUTTONUP:
                EventManager._mouse_event(event)
            case sdl2.SDL_MOUSEWHEEL:
                EventManager._mouse_scroll_wheel_event(event)
            case sdl2.SDL_CONTROLLERDEVICEADDED | sdl2.SDL_CONTROLLERDEVICEREMOVED | sdl2.SDL_CONTROLLERAXISMOTION | sdl2.SDL_CONTROLLERBUTTONDOWN | sdl2.SDL_CONTROLLERBUTTONUP:  # noqa
                EventManager._controller_event(event)
            case sdl2.SDL_RENDER_TARGETS_RESET | sdl2.SDL_RENDER_DEVICE_RESET:
                EventManager._render_reset_event()

    @staticmethod
    def _quit_event() -> None:
        """ Handle a quit event. """
        from potion.engine import Engine
        Engine.on_quit_requested()

    @staticmethod
    def _window_event(event: sdl2.SDL_Event) -> None:
        """ Handle any window event. """
        match event.window.event:
            case sdl2.SDL_WINDOWEVENT_RESIZED:
                Window.on_window_resized()
            case sdl2.SDL_WINDOWEVENT_ENTER:
                InputManager.register_mouse_enter_window()
            case sdl2.SDL_WINDOWEVENT_LEAVE:
                InputManager.register_mouse_leave_window()

    @staticmethod
    def _keyboard_event(event: sdl2.SDL_Event) -> None:
        """ Handle a keyboard event. """
        # Treat key repeats separately (when a key is held down)
        if event.key.repeat != 0:
            InputManager.register_key_repeat(event.key.keysym.sym)
            return

        match event.type:
            case sdl2.SDL_KEYDOWN:
                InputManager.register_key_down(event.key.keysym.sym)
            case sdl2.SDL_KEYUP:
                InputManager.register_key_up(event.key.keysym.sym)

    @staticmethod
    def _text_input_event(event: sdl2.SDL_Event) -> None:
        """ Handle a text input event. """
        InputManager.register_text_input(event.text.text.decode())

    @staticmethod
    def _mouse_event(event: sdl2.SDL_Event) -> None:
        """ Handle a mouse event. """
        match event.type:
            case sdl2.SDL_MOUSEBUTTONDOWN:
                InputManager.register_mouse_down(event.button.button)
            case sdl2.SDL_MOUSEBUTTONUP:
                InputManager.register_mouse_up(event.button.button)

    @staticmethod
    def _mouse_scroll_wheel_event(event: sdl2.SDL_Event) -> None:
        """ Handle a mouse wheel event. """
        InputManager.register_mouse_scroll_wheel(event.wheel.y)

    @staticmethod
    def _controller_event(event: sdl2.SDL_Event) -> None:
        """ Handle a controller event. """
        match event.type:
            case sdl2.SDL_CONTROLLERDEVICEADDED:
                InputManager.register_controller_added(event.cdevice.which)
            case sdl2.SDL_CONTROLLERDEVICEREMOVED:
                InputManager.register_controller_removed(event.cdevice.which)
            case sdl2.SDL_CONTROLLERAXISMOTION:
                InputManager.register_controller_axis_motion(event.caxis.which, event.caxis.axis, event.caxis.value)
            case sdl2.SDL_CONTROLLERBUTTONDOWN:
                InputManager.register_controller_button_down(event.cbutton.which, event.cbutton.button)
            case sdl2.SDL_CONTROLLERBUTTONUP:
                InputManager.register_controller_button_up(event.cbutton.which, event.cbutton.button)

    @staticmethod
    def _render_reset_event() -> None:
        """ Handle a render targets reset or render device reset event. """
        Renderer.on_renderer_reset()
