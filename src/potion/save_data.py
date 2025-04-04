import base64
import json

from ulid import ULID

from potion.file_manager import FileManager
from potion.log import Log


class SaveData:
    """ Save and load game data. """
    @classmethod
    def exists(cls, save_file_name: str) -> bool:
        """ Check if a save file exists. """
        return save_file_name in cls.list()

    @classmethod
    def list(cls) -> list[str]:
        """ Return a list of saved game files. """
        files = []

        if not FileManager.saves_folder().exists():
            return files

        for file in FileManager.saves_folder().iterdir():
            if file.suffix == ".psav":
                files.append(file.stem)

        return files

    @classmethod
    def save(cls, save_file_name: str, data: dict) -> None:
        """ Save to disk. """
        file = (FileManager.saves_folder() / save_file_name).with_suffix(".psav")
        temp_file = (FileManager.saves_folder() / save_file_name).with_suffix(f".{ULID()}.temp")

        # Create directory
        FileManager.saves_folder().mkdir(parents=True, exist_ok=True)

        # Convert data to JSON
        try:
            json_data = json.dumps(data).encode("utf-8")
        except TypeError as e:
            Log.error(f"Could not save game data: {e}")
            return

        # Save to temp file
        with temp_file.open('wb') as fp:
            encoded_data = base64.b64encode(json_data)
            fp.write(encoded_data)

        # Swap temp with real file
        temp_file.replace(file)

    @classmethod
    def load(cls, save_file_name: str) -> dict:
        """ Load a save from disk. """
        file = (FileManager.saves_folder() / save_file_name).with_suffix(".psav")
        data = {}

        # Make sure file exists
        if not file.exists():
            Log.error(f"Save file does not exist: {file.as_posix()}")
            return data

        # Read from file
        with file.open('rb') as fp:
            encoded_data = fp.read()
            decoded_data = base64.b64decode(encoded_data).decode("utf-8")
            data = json.loads(decoded_data)

        return data

    @classmethod
    def delete(cls, save_file_name: str) -> None:
        """ Delete a save file. """
        file = (FileManager.saves_folder() / save_file_name).with_suffix(".psav")

        if not file.exists():
            Log.error(f"Save file does not exist: {file.as_posix()}")
            return

        Log.debug(f"Deleting save file: {file.as_posix()}")
        file.unlink()
