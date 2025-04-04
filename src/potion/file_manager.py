import os
import platform
from pathlib import Path

from potion.game import Game


class FileManager:
    """ Get common file paths. """
    @classmethod
    def game_data_root(cls) -> Path:
        """ Get the path to the root directory for all game data.

        Windows:
            ./AppData/Local/GameName/

        MacOS and Linux:
            ~/.GameName
        """
        game_name = Game.clean_name()

        # On Windows, try to save in the AppData/Local path
        if platform.system() == "Windows":
            if appdata := os.getenv("LOCALAPPDATA"):
                appdata_path = Path(appdata)
                if appdata_path.is_dir():
                    return appdata_path / game_name

        return Path.home() / f".{game_name}"

    @classmethod
    def saves_folder(cls) -> Path:
        """ The folder for saved games. """
        return cls.game_data_root() / "Saves"

    @classmethod
    def logs_folder(cls) -> Path:
        """ The folder for log files. """
        return cls.game_data_root() / "Logs"

    @classmethod
    def crash_logs_folder(cls) -> Path:
        """ The folder for crash log files. """
        return cls.game_data_root() / "CrashLogs"
