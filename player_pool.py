from player import Player
from discord import utils
from discord.voice_client import VoiceClient
from discord.ext.commands import Bot

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