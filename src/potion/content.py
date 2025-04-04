import sys
import zipfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, IO, Iterator

from potion.content_types.audio_clip import AudioClip
from potion.content_types.audio_stream import AudioStream
from potion.content_types.texture import Texture
from potion.log import Log
from potion.utilities import papp


class Content:
    """ Load content into the engine.  """

    # The folder to search for content. This is folder called "content" relative to the working directory.
    # The dynamic behavior is required for PyInstaller to handle file paths correctly.
    if papp.is_pyinstaller():
        __content_root = Path(sys._MEIPASS)  / "content" # noqa
    else:
        __content_root = Path.cwd() / "content"

    # The content root may be a folder or a zip file
    if zipfile.is_zipfile(__content_root):
        __is_zip = True
        __content_root = zipfile.Path(__content_root)
    else:
        __is_zip = False

    # Loaded content is cached so that it can be quickly returned at runtime.
    __loaded_content: dict[str, Any] = {}

    @classmethod
    def root(cls) -> Path:
        """ Get the content root. """
        return cls.__content_root

    @classmethod
    def parent(cls, content_path: str) -> str:
        """ Get the parent of a content path.
        If the parent is the content root, this function returns an empty string.
        """
        content_path = cls._format_path(content_path)
        return Path(content_path).parent.as_posix()

    @classmethod
    def suffix(cls, content_path: str) -> str:
        """ Get the file extension of a content path. """
        content_path = cls._format_path(content_path)
        return Path(content_path).suffix

    @classmethod
    def with_suffix(cls, content_path: str, suffix: str) -> str:
        """ Get a content path with the suffix changed. """
        content_path = cls._format_path(content_path)
        return Path(content_path).with_suffix(suffix).as_posix()

    @classmethod
    def stem(cls, content_path: str) -> str:
        """ Get the file name of a content path, without its suffix. """
        content_path = cls._format_path(content_path)
        return Path(content_path).stem

    @classmethod
    def exists(cls, content_path: str) -> bool:
        """ Check if a content path exists. """
        content_path = cls._format_path(content_path)
        full_content_path = cls._full_content_path(content_path)
        return full_content_path.exists()

    @classmethod
    def is_file(cls, content_path: str) -> bool:
        """ Check if a content path is a file. """
        content_path = cls._format_path(content_path)
        full_content_path = cls._full_content_path(content_path)
        return full_content_path.is_file()

    @classmethod
    def is_dir(cls, content_path: str) -> bool:
        """ Check if a content path is a directory. """
        content_path = cls._format_path(content_path)
        full_content_path = cls._full_content_path(content_path)
        return full_content_path.is_dir()

    @classmethod
    def iterdir(cls, content_path: str | None = None) -> Iterator[Path]:
        """ Iterate over the children of a content path.
        If content_path is not provided, the operation will be performed from the content root.
        """
        content_path = cls._format_path(content_path)
        if not content_path:
            full_content_path = cls.__content_root
        else:
            full_content_path = cls._full_content_path(content_path)

        for item in full_content_path.iterdir():
            yield item

    @classmethod
    @contextmanager
    def open(cls, content_path: str, mode: str = 'r') -> IO:
        content_path = cls._format_path(content_path)
        full_content_path = cls._full_content_path(content_path)
        with full_content_path.open(mode=mode) as fp:
            yield fp

    @classmethod
    def is_loaded(cls, content_path: str) -> bool:
        """ Returns True if content at the path is loaded. """
        return content_path in cls.__loaded_content

    # noinspection DuplicatedCode
    @classmethod
    def load_audio_clip(cls, content_path: str) -> AudioClip:
        """ Load an audio clip. """
        content_path = cls._format_path(content_path)
        if content_path not in cls.__loaded_content:
            if cls.exists(content_path):
                full_content_path = cls._full_content_path(content_path)
                cls.__loaded_content[content_path] = AudioClip.from_file(full_content_path)
            else:
                Log.error(f"Content path does not exist: {content_path}")
                cls.__loaded_content[content_path] = AudioClip.create_empty()

        return cls.__loaded_content[content_path]

    # noinspection DuplicatedCode
    @classmethod
    def load_audio_stream(cls, content_path: str) -> AudioStream:
        """ Load an audio stream. """
        content_path = cls._format_path(content_path)
        if content_path not in cls.__loaded_content:
            if cls.exists(content_path):
                full_content_path = cls._full_content_path(content_path)
                cls.__loaded_content[content_path] = AudioStream.from_file(full_content_path)
            else:
                Log.error(f"Content path does not exist: {content_path}")
                cls.__loaded_content[content_path] = AudioStream.create_empty()

        return cls.__loaded_content[content_path]

    @classmethod
    def load_texture(cls, content_path: str) -> Texture:
        """ Load a 2D texture. """
        content_path = cls._format_path(content_path)
        if content_path not in cls.__loaded_content:
            if cls.exists(content_path):
                full_content_path = cls._full_content_path(content_path)
                cls.__loaded_content[content_path] = Texture.from_file(full_content_path)
            else:
                Log.error(f"Content path does not exist: {content_path}")
                cls.__loaded_content[content_path] = Texture.create_static(2, 2)

        return cls.__loaded_content[content_path]

    @classmethod
    def reload(cls) -> None:
        """ Reload content. """
        # Get the types of the loaded content
        content_types = []
        for content_path, content_obj in cls.__loaded_content.items():
            content_types.append((content_path, type(content_obj)))

        # Clear the loaded content
        cls.__loaded_content.clear()

        # Reload each content path by type
        for content_path, content_type in content_types:
            if content_type is AudioClip:
                cls.load_audio_clip(content_path)
            elif content_type is AudioStream:
                cls.load_audio_stream(content_path)
            elif content_type is Texture:
                cls.load_texture(content_path)
            else:
                Log.error(f"Error reloading '{content_path}'; content type '{content_type}' unsupported")

    @classmethod
    def unload(cls, content_path: str) -> None:
        """ Unload content. """
        content_path = cls._format_path(content_path)
        try:
            cls.__loaded_content.pop(content_path)
        except KeyError:
            Log.error(f"Content path has not been loaded: {content_path}")

    @classmethod
    def _full_content_path(cls, content_path: str) -> Path | zipfile.Path:
        """ Convert a content path string to a full Path object. """
        content_path = cls._format_path(content_path)
        return cls.__content_root / content_path

    @classmethod
    def _format_path(cls, content_path: str) -> str:
        """ Format a content path for consistency. """
        p = content_path

        # Remove
        if p.startswith("./"):
            p = p[2:]

        # Remove leading and trailing slashes
        p = p.strip("/")

        # Turn a period into an empty string
        if p == ".":
            p = ""

        return p
