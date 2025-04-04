import sdl2.sdlmixer

from potion.content import Content


class SoundEffect:
    """ A short form audio clip. """
    def __init__(self, content_path: str) -> None:
        """ `content_path` is the path to the audio file. """
        self._name = content_path
        self._audio_clip = Content.load_audio_clip(content_path)

    def __str__(self) -> str:
        return f"SoundEffect({self._name})"

    def __repr__(self) -> str:
        return str(self)

    def play(self) -> None:
        """ Play the audio clip. """
        sdl2.sdlmixer.Mix_PlayChannel(channel=-1, chunk=self._audio_clip.sdl_mix_chunk, loops=0)
