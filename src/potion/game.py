from potion.utilities import pstring


class Game:
    """ Information about the game. """
    _initialized = False

    _name: str = ""
    _clean_name: str = ""
    _version: str = ""

    @classmethod
    def init(cls, name: str, version: str) -> None:
        """ Initialize the game. """
        if cls._initialized:
            raise RuntimeError("The game has already been initialized.")

        name = name.strip()
        clean_name = pstring.remove_special_characters(name)
        version = version.strip()

        if not name:
            raise RuntimeError("Game name cannot be empty")

        if not clean_name:
            raise RuntimeError("Clean name cannot be empty")

        if not version:
            raise RuntimeError("Version cannot be empty")

        cls._name = name
        cls._clean_name = clean_name
        cls._version = version

        cls._initialized = True

    @classmethod
    def ensure_init(cls) -> None:
        """ Make sure the game has been initialized. """
        if not cls._initialized:
            raise RuntimeError("The game has not been initialized. Make sure to run `Game.init()`.")

    @classmethod
    def name(cls) -> str:
        """ The name of the game. """
        return cls._name

    @classmethod
    def clean_name(cls) -> str:
        """ The clean name of the game, without any special characters. """
        return cls._clean_name

    @classmethod
    def version(cls) -> str:
        """ The version of the game. """
        return cls._version
