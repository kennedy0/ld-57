from __future__ import annotations

from io import BytesIO
from pathlib import Path

import sdl2
import sdl2.sdlmixer


class AudioClip:
    """ A wrapper around SDL_mixer Mix_Chunk.

    New instances of this shouldn't be created manually, instead the factory methods should be used to more easily
    initialize the audio clip.
    """
    def __init__(self, name: str, rw: sdl2.SDL_RWops) -> None:
        self._name = name
        self._sdl_mix_chunk = sdl2.sdlmixer.Mix_LoadWAV_RW(rw, freesrc=True)

    def __del__(self) -> None:
        sdl2.sdlmixer.Mix_FreeChunk(self._sdl_mix_chunk)

    def __str__(self) -> str:
        return f"AudioClip({self._name})"

    def __repr__(self) -> str:
        return str(self)

    @property
    def sdl_mix_chunk(self) -> sdl2.sdlmixer.Mix_Chunk:
        return self._sdl_mix_chunk

    @classmethod
    def create_empty(cls) -> AudioClip:
        """ Create an empty audio stream. """
        rw = sdl2.rw_from_object(BytesIO())
        return cls("empty", rw)

    @classmethod
    def from_file(cls, audio_file: Path) -> AudioClip:
        """ Create an audio clip from an audio file. """
        fp = audio_file.open('rb')
        rw = sdl2.rw_from_object(BytesIO(fp.read()))
        return cls(audio_file.name, rw)
