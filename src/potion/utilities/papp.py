import datetime
import os
import traceback
import platform
import sys
from contextlib import contextmanager
from ctypes import byref, c_int
from pathlib import Path
from typing import Generator


def is_pyinstaller() -> bool:
    """ Check if we are running with PyInstaller. """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return True

    return False


@contextmanager
def crash_handler() -> Generator:
    """ Context manager to handle any application crashes. """
    try:
        yield
    except Exception as e:  # noqa
        # Don't write crash log in debug mode
        if __debug__:
            if is_pyinstaller():
                traceback.print_exc()
                input("\nPress ENTER or close this window to quit...")
                sys.exit(1)
            else:
                raise e

        from potion.file_manager import FileManager
        from potion.game import Game

        # Write crash log
        FileManager.crash_logs_folder().mkdir(parents=True, exist_ok=True)
        crash_log = FileManager.crash_logs_folder() / datetime.datetime.now().strftime("crash.%Y%m%d_%H%M%S.log")
        with crash_log.open('w') as fp:
            fp.write(traceback.format_exc())

        # Show window
        import sdl2
        title = f"{Game.name()} Crashed"
        message = f"Uh-oh, {Game.name()} crashed :(\nA crash log was written here:\n{crash_log.as_posix()}"
        button_data = [
            sdl2.SDL_MessageBoxButtonData(
                sdl2.SDL_MESSAGEBOX_BUTTON_RETURNKEY_DEFAULT | sdl2.SDL_MESSAGEBOX_BUTTON_ESCAPEKEY_DEFAULT,
                0,
                "Close".encode("utf-8")
            ),
            sdl2.SDL_MessageBoxButtonData(
                0,
                1,
                "Open Folder".encode("utf-8")
            ),
        ]
        button_data_array = (sdl2.SDL_MessageBoxButtonData * len(button_data))(*button_data)
        message_box_data = sdl2.SDL_MessageBoxData(
            sdl2.SDL_MESSAGEBOX_ERROR,  # flags
            None,                       # window
            title.encode("utf-8"),      # title
            message.encode("utf-8"),    # message
            2,                          # numbuttons
            button_data_array,          # buttons
            None,                       # color scheme
        )
        button = c_int()
        sdl2.SDL_ShowMessageBox(message_box_data, byref(button))

        if button.value == 1:
            open_folder(FileManager.crash_logs_folder())

        # Return error code
        sys.exit(1)


def open_folder(folder: Path) -> None:
    """ Open a folder in the file browser. """
    if platform.system() == "Windows":
        os.startfile(folder)
    else:
        pass
