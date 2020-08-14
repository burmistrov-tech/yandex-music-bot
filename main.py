import json
import logging
from audio import Audio
from player_pool import PlayerPool
from yandex_music import Client
from discord.ext.commands import Bot

with open('settings.json', 'r') as f:
    data = json.load(f)

TOKEN = data['discord']['token']
BOT_PREFIX = data['discord']['prefix']
LOGIN = data['yandex-music']['login']
PASSWORD = data['yandex-music']['password'] 

y_client = Client.fromCredentials(LOGIN, PASSWORD)
logging.basicConfig(level=logging.CRITICAL)


bot = Bot(command_prefix=BOT_PREFIX)
player_pool = PlayerPool(bot)

@bot.event
async def on_ready():
    print('Logged in ' + bot.user.name + '\n')

@bot.command(aliases=['j', 'jo'])
async def join(ctx):
    if not ctx.author.voice:
        await ctx.send(f'You are not in any channel')

    voice_channel = ctx.author.voice.channel
    if not ctx.voice_client:
        voice_client = await voice_channel.connect()
    else:
        await voice_client.move_to(voice_channel)
          
    await ctx.send(f'{bot.user.name} has connected to {voice_channel}')

 
@bot.command(aliases=['l', 'lv'])
async def leave(ctx):
    if ctx.author.voice is None:
        await ctx.send('You are not in any channel')        
    
    if ctx.me.voice is None:
        await ctx.send('I am not in one channel.\nUse bot.join to connect')

    voice_channel = ctx.author.voice.channel
    await ctx.voice_client.disconnect()
    await ctx.send(f'{bot.user.name} has left {voice_channel}')

@bot.command(aliases=['p', 'pl'])
async def play(ctx, *args):    
    if ctx.author.voice is None:
        await ctx.send('You are not in any channel')
        return
    
    if ctx.me.voice is None:
        await join(ctx)

    if ctx.author.voice.channel != ctx.me.voice.channel:
        await ctx.send('You have to be in the same channel')
        return
    
    player = player_pool.get(ctx.guild)
    search_str = ' '.join(args)    
    search_result = y_client.search(search_str)
    track = search_result.tracks.results[0]    
    audio = Audio(track)
    await player.play(audio)

@bot.command()
async def playlist(ctx, *args):    
    if ctx.author.voice is None:
        await ctx.send('You are not in any channel')
        return
    
    if ctx.me.voice is None:
        await join(ctx)

    if ctx.author.voice.channel != ctx.me.voice.channel:
        await ctx.send('You have to be in the same channel')        
        return

    player = player_pool.get(ctx.guild)
    try:
        search_args = [str(args[0]), int(args[1])]
    except Exception as ex:
        raise(ex)        

    search_result = y_client.users_playlists_list(search_args[0])
    playlist = search_result[0]
    await ctx.send('Downloading tracks')

    short_tracks = y_client.users_playlists(search_args[1], playlist.uid)[0].tracks
    tracks_id = [st.track_id for st in short_tracks]
    tracks = y_client.tracks(tracks_id)
    audio = [Audio(t) for t in tracks]

    await player.playlist(audio)

          
@bot.command(aliases=['pau', 'ps'])
async def pause(ctx): 
    player = player_pool.get(ctx.guild)
    await player.pause()
    await ctx.send("Music has stopped")

@bot.command(aliases=['clr'])
async def clear(ctx): 
    player = player_pool.get(ctx.guild)
    await player.clear()
    await ctx.send("Queue is clear")

@bot.command(aliases=['n', 'skip'])
async def next(ctx):
    player = player_pool.get(ctx.guild)
    await player.next()
    await ctx.send("Next track")

@bot.command(aliases=['r', 'rsm'])
async def resume(ctx): 
    player = player_pool.get(ctx.guild)
    await player.resume()
    await ctx.send("Music has resumed")

#future
def catch(self, *args, **kwargs):
    try:
        def decorator(func):            
            func()
    except expression as identifier:
        pass 
    
    return decorator

if __name__ == "__main__":    
    bot.run(TOKEN)