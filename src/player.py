import random
import asyncio
from typing import List

from yandex_music import Track
from discord.voice_client import VoiceClient
from discord.ext.commands import Bot

from .audio import Audio
from .extended.errors import PlayerInvalidState, PlayerInvalidVolume, PlayerQueueEmpty, MissingInChannel

class Player():        
    def __init__(self, voice_client: VoiceClient):
        self.voice_client = voice_client
        self.audio_list = list()
        self._state = asyncio.Event()
        self._volume = 0.5 

    def toogle_next(self, error: Exception = None, *args):
        self._state.set()
        if error:
            raise(error)

    async def _run(self):
        while self.audio_list:
            self._state.clear()   
            audio = self.audio_list.pop(0)
            source = audio.get()
            source.volume = self.volume         
            self.voice_client.play(source, after = self.toogle_next)
            print(f'voice client начал проигрывание {audio.track.title}')
            await self._state.wait() 

    @property
    def volume(self):
        return self._volume
    
    @volume.setter
    def volume(self, value: float):
        if not 0 <= value <= 100:                    
            raise PlayerInvalidVolume('The value have to be between 0 and 100')        
        
        self._volume = value / 100
        if self.is_playing():
            self.voice_client.source.volume = self.volume
           
    @property
    def is_playing(self) -> bool:
        return self.voice_client.is_playing()
    @property
    def is_paused(self) -> bool:                    
        return self.voice_client.is_paused()
    @property
    def is_empty(self) -> bool:        
        return len(self.audio_list) > 0
    
    async def play(self, audio: Audio):
        self.audio_list.append(audio)

        if not self.is_playing:
            await self._run()

    async def playlist(self, audio: List[Audio]):
        self.audio_list.extend(audio)
        
        if not self.is_playing:
            await self._run()   

    async def pause(self):
        if self.is_playing:
            raise PlayerInvalidState('Bot is not playing')

        self.voice_client.pause()
    
    async def resume(self):
        if self.is_paused:
            raise PlayerInvalidState('Bot has not paused')

        self.voice_client.resume()

    async def stop(self):
        try:
            await self.clear()
        finally:
            if self.is_playing or self.is_paused:
                self.voice_client.stop()
            else:
                raise PlayerInvalidState('Bot is not playing or paused')        
            
    async def skip(self):
        if self.is_playing or self.is_paused:
            self.voice_client.stop()
        else:
            raise PlayerInvalidState('Bot is not playing or paused')

    async def shuffle(self):
        if self.is_empty:
            raise PlayerQueueEmpty()

        random.shuffle(self.audio_list)

    async def queue(self, amount: int = 10) -> List[Audio]:
        return self.audio_list[:amount]
        
    async def clear(self):
        if self.is_empty:
            raise PlayerQueueEmpty()

        self.audio_list.clear()

class PlayerPool():
    def __init__(self, bot: Bot):
        self.bot = bot
        self.players = dict()        

    def get(self, guild, *args) -> Player:
        from discord.utils import get
        voice_client = get(self.bot.voice_clients, guild=guild)

        if voice_client is None:
            raise MissingInChannel('Bot not in the channel')

        player = self.players.get(guild)        
        if not player or player.voice_client != voice_client:
            player = Player(voice_client)
            self.players[guild] = player

        return player