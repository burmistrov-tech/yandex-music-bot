from audio import Audio
from typing import List
from asyncio import Event
from yandex_music import Track
from discord import utils
from discord.voice_client import VoiceClient
from discord.ext.commands import Bot, check, CheckFailure

class Player():        
    def __init__(self, voice_client: VoiceClient):
        self.voice_client = voice_client
        self.state = Event()
        self.audio_list = list()
    
    async def _run(self):
        while self.audio_list:
            self.state.clear()   
            audio = self.audio_list.pop(0)
            source = audio.get()
            self.voice_client.play(source, after = self.toogle_next) 
            print(f'voice client начал проигрывание {audio.track.title}')
            await self.state.wait() 

    def toogle_next(self, error = None, *args):
        self.state.set()
        if error:
            raise(error)                

    def is_playing(self, exception = True):
        if not self.voice_client.is_playing():
            if exception:            
                raise CheckFailure('Bot is not playing')
            return False
        return True

    def is_paused(self, exception = True):                    
        if not self.voice_client.is_paused():
            if exception:                
                raise CheckFailure('Bot has not paused')            
            return False
        return True

    def is_empty(self, exception = True):        
        if not len(self.audio_list):
            if exception:
                raise CheckFailure('No music in the queue')
            return False
        return True

    async def play(self, audio: Audio):
        self.audio_list.append(audio)
        if not self.is_playing(exception=False):
            await self._run()

    async def playlist(self, audio: List[Audio]):
        self.audio_list.extend(audio)
        if not self.is_playing(exception=False):
            await self._run()

    async def clear(self):
        self.is_empty()
        self.audio_list.clear()

    async def pause(self):
        self.is_playing()
        self.voice_client.pause()
    
    async def resume(self):
        self.is_paused()
        self.voice_client.resume()
        
    async def next(self):
        self.voice_client.stop()        

    # future
    async def queue(self):
        pass

    # future
    async def volume(self):
        pass

    # future
    async def shuffle(self):
        pass

class PlayerPool():
    def __init__(self, bot: Bot):
        self.bot = bot
        self.players = dict()        

    def get(self, guild, *args) -> Player:
        voice_client = utils.get(self.bot.voice_clients, guild=guild)

        if not voice_client:
            raise ValueError("Bot not in the channel")

        player = self.players.get(guild)        
        if not player or player.voice_client != voice_client:
            player = Player(voice_client)
            self.players[guild] = player

        return player