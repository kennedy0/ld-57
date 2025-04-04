import ctypes

import sdl2


class Clipboard:
    """ Get and set clipboard contents. """
    @staticmethod
    def get_text() -> str:
        """ Get clipboard text. """
        if not sdl2.SDL_HasClipboardText():
            return ""

        # Change the restype of the clipboard text so that the pointer can be freed
        # https://github.com/py-sdl/py-sdl2/issues/128
        old_restype = sdl2.SDL_GetClipboardText.restype
        sdl2.SDL_GetClipboardText.restype = ctypes.c_char_p
        text_ptr = sdl2.SDL_GetClipboardText()
        sdl2.SDL_GetClipboardText.restype = old_restype

        if text_ptr == 0:
            return ""

        text = ctypes.cast(text_ptr, ctypes.c_char_p).value.decode("utf-8")
        sdl2.SDL_free(text_ptr)
        return text

    @staticmethod
    def set_text(text: str) -> None:
        """ Set clipboard text. """
        sdl2.SDL_SetClipboardText(text.encode("utf-8"))
