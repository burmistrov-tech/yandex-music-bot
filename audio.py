import os
from yandex_music import Track
from discord import FFmpegPCMAudio, PCMVolumeTransformer

class Audio():
    def __init__(self, track: Track):
        self.track = track

    @property
    def file_name(self) -> str:
        if self.track.albums:
            return f'{self.track.id}_{self.track.albums[0].id}.mp3'

        return f"{self.track.id}.mp3"
    
    @property
    def full_title(self) -> str:
        title = self.track.title
        artists = ', '.join(a.name for a in self.track.artists if a.name)
        
        return f'{title} {artists}'

    def get(self) -> PCMVolumeTransformer:
        if not os.path.isfile(self.file_name):
            self.track.download(self.file_name)

        return PCMVolumeTransformer(FFmpegPCMAudio(self.file_name))