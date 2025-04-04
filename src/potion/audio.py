import sdl2.sdlmixer

from potion.utilities import pmath


class Audio:
    """ Audio settings. """
    @classmethod
    def music_volume(cls) -> int:
        """ Get the music volume. """
        return sdl2.sdlmixer.Mix_VolumeMusic(-1)

    @classmethod
    def set_music_volume(cls, volume: int) -> None:
        """ Set the music volume (0-128 range). """
        clamped_volume = pmath.clamp(volume, 0, sdl2.sdlmixer.MIX_MAX_VOLUME)
        sdl2.sdlmixer.Mix_VolumeMusic(clamped_volume)

    @classmethod
    def sfx_volume(cls) -> int:
        """ Get the SFX volume. """
        return sdl2.sdlmixer.Mix_MasterVolume(-1)

    @classmethod
    def set_sfx_volume(cls, volume: int) -> None:
        """ Set the music volume (0-128 range). """
        clamped_volume = pmath.clamp(volume, 0, sdl2.sdlmixer.MIX_MAX_VOLUME)
        sdl2.sdlmixer.Mix_MasterVolume(clamped_volume)
