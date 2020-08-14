from audio import Audio
from typing import List
from asyncio import Event
from yandex_music import Track
from discord import utils
from discord.voice_client import VoiceClient

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

    async def play(self, audio: Audio):
        self.audio_list.append(audio)
        if not self.voice_client.is_playing():
            await self._run()

    async def playlist(self, audio: List[Audio]):
        self.audio_list.extend(audio)
        if not self.voice_client.is_playing():
            await self._run()

    async def clear(self):
        if not len(self.audio_list):
            raise Exception("No music in the queue")

        self.audio_list.clear()

    async def pause(self):
        if not self.voice_client.is_playing():
            raise Exception("Bot is not playing")
        
        self.voice_client.pause()

    async def resume(self):
        if not self.voice_client.is_paused():
            raise Exception("Bot has not paused")
        
        self.voice_client.resume()
    
    # future
    async def next(self):
        if not self.voice_client.is_playing():
            raise Exception("Bot is not playing")
        
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