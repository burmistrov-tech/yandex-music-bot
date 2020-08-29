import os

from yandex_music import Track
from discord import FFmpegPCMAudio, PCMVolumeTransformer


class Audio():
    def __init__(self, track: Track):
        self.track = track

    def __str__(self):
        return self.full_title

    @property
    def full_title(self) -> str:
        title = self.track.title
        artists = ', '.join(a.name for a in self.track.artists if a.name)
        return f'{title} - {artists}'

    @property
    def file_name(self) -> str:
        if self.track.albums:
            return f'{self.track.id}_{self.track.albums[0].id}.mp3'

        return f"{self.track.id}.mp3"

    def get(self) -> PCMVolumeTransformer:
        if not os.path.isfile(self.file_name):
            self.track.download(self.file_name, bitrate_in_kbps=192)

        return PCMVolumeTransformer(FFmpegPCMAudio(self.file_name))
