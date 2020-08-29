import json
import logging
from yandex_music import Client

from src.bot import MusicBot
from src.commands import BotCommands

with open('config.json', 'r') as f:
    data = json.load(f)

TOKEN = data['discord']['token']
BOT_PREFIX = data['discord']['prefix']
LOGIN = data['yandex-music']['login']
PASSWORD = data['yandex-music']['password'] 

y_client = Client.fromCredentials(LOGIN, PASSWORD)
bot = MusicBot(command_prefix=BOT_PREFIX, yandex_client=y_client)
bot.add_cog(BotCommands(bot, y_client))

if __name__ == "__main__":
    bot.run(TOKEN)