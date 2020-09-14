import time
import random
import asyncio
import threading
from typing import List

from yandex_music import Track
from discord.player import AudioPlayer
from discord.voice_client import VoiceClient, opus
from discord.ext.commands import Bot

from .audio import YandexAudioSource
from ..extended.errors import PlayerInvalidState, PlayerInvalidVolume, \
    PlayerQueueEmpty, MissingInChannel


class YandexAudioPlayer(AudioPlayer):
    def __init__(self, client, *, after=None):
        threading.Thread.__init__(self)
        client.encoder = opus.Encoder()

        self.daemon = True
        self.client = client
        self.after = after
        self.source = None
        self.sources = list()

        self._volume = 0.5
        self._end = threading.Event()
        self._resumed = threading.Event()
        self._resumed.set()  # we are not paused
        self._skip = False
        self._current_error = None
        self._connected = client._connected
        self._lock = threading.Lock()

        if after is not None and not callable(after):
            raise TypeError('Expected a callable for the "after" parameter.')

    def _do_run(self):
        while not self.is_empty():
            self.source = self.sources.pop(0)
            self.source.volume = self.volume
            self.loops = 0
            self._speak(True)
            self._start = time.perf_counter()
            while not self._end.is_set():
                data = self.source.read()

                if not data or self._skip:
                    self._skip = False
                    break

                if not self._resumed.is_set():
                    self._resumed.wait()
                    continue

                if not self._connected.is_set():
                    self._connected.wait()
                    self.loops = 0
                    self._start = time.perf_counter()

                self.loops += 1
                self.client.send_audio_packet(data, encode=not self.source.is_opus())
                next_time = self._start + self.DELAY * self.loops
                delay = max(0, self.DELAY + (next_time - time.perf_counter()))
                time.sleep(delay)

            self.source.cleanup()
            print('End playng track')
        print('End playing tracks')

    @property
    def volume(self):
        return self._volume * 100

    @volume.setter
    def volume(self, value: float):
        if not 0 <= value <= 100:
            raise PlayerInvalidVolume('The value have to be between 0 and 100')

        self._volume = value / 100
        if self.is_playing():
            self.source.volume = self._volume

    def is_empty(self) -> bool:
        return len(self.sources) == 0

    def play(self, source: YandexAudioSource):
        self.sources.append(source)

        if not self.is_alive():
            self.start()

    def playlist(self, sources: List[YandexAudioSource]):
        self.sources.extend(sources)

        if not self.is_alive():
            self.start()

    def pause(self, *, update_speaking=True):
        if not self.is_playing():
            raise PlayerInvalidState('Bot is not playing')

        super().pause(update_speaking=update_speaking)

    def resume(self, *, update_speaking=True):
        if not self.is_paused():
            raise PlayerInvalidState('Bot has not paused')

        super().resume(update_speaking=update_speaking)

    def stop(self, clear_queue=False):
        if self.is_playing() or self.is_paused():
            if clear_queue:
                try:
                    self.clear()
                except PlayerQueueEmpty:
                    pass
            super().stop()
        else:
            raise PlayerInvalidState('Bot is not playing or paused')

    def skip(self):
        if self.is_playing() or self.is_paused():
            self._skip = True
        else:
            raise PlayerInvalidState('Bot is not playing or paused')

    def shuffle(self):
        if self.is_empty():
            raise PlayerQueueEmpty()

        random.shuffle(self.sources)

    def queue(self, amount: int = 10) -> List[YandexAudioSource]:
        return self.sources[:amount]

    def clear(self):
        if self.is_empty():
            raise PlayerQueueEmpty()

        self.sources.clear()


class YandexAudioPlayerPool:
    def find(self, client) -> YandexAudioPlayer:
        for thread in threading.enumerate():
            if thread.name == client.session_id:
                return thread

        return None

    def register(self, client):
        player = YandexAudioPlayer(client)
        player.setName(client.session_id)

        return player
