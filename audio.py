import os
from yandex_music import Track
from discord import FFmpegPCMAudio

class Audio():
    def __init__(self, track: Track):
        self.track = track

    @property
    def file_name(self) -> str:
        if self.track.albums:
            return f"{self.track.id}_{self.track.albums[0].id}.mp3"

        return f"{self.track.id}.mp3"

    def get(self) -> FFmpegPCMAudio:
        if not os.path.isfile(self.file_name):
            self.track.download(self.file_name)

        return FFmpegPCMAudio(self.file_name)