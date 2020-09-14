import os
import audioop

from yandex_music import Track
from discord import FFmpegPCMAudio, PCMVolumeTransformer


class YandexAudioSource(PCMVolumeTransformer):
    def __init__(self, track: Track, volume=0.5):
        self.track = track
        self.volume = volume
        self.original = None
        self._is_downloaded = False

    def __str__(self):
        return self.full_title

    @property
    def full_title(self) -> str:
        title, artists = self.track.title, ', '.join(
            a.name for a in self.track.artists if a.name)

        return f'{title} - {artists}'

    @property
    def file_name(self) -> str:
        if self.track.albums:
            return f'{self.track.id}_{self.track.albums[0].id}.mp3'

        return f"{self.track.id}.mp3"

    def download(self):
        if not os.path.isfile(self.file_name):
            self.track.download(self.file_name, bitrate_in_kbps=192)

        self.original = FFmpegPCMAudio(self.file_name)
        self._is_downloaded = True

    def cleanup(self):
        if self._is_downloaded:
            self.original.cleanup()

    def read(self):
        if not self._is_downloaded:
            self.download()

        return super().read()
