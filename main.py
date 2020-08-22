import json
import logging
from audio import Audio
from itertools import count
from yandex_music import Client
from discord.ext.commands import Bot, check, CheckFailure
from player import *

with open('config.json', 'r') as f:
    data = json.load(f)

TOKEN = data['discord']['token']
BOT_PREFIX = data['discord']['prefix']
LOGIN = data['yandex-music']['login']
PASSWORD = data['yandex-music']['password'] 

y_client = Client.fromCredentials(LOGIN, PASSWORD)
logging.basicConfig(level=logging.CRITICAL)


bot = Bot(command_prefix=BOT_PREFIX)
player_pool = PlayerPool(bot)

async def author_in_channel(ctx):
    if not ctx.author.voice:
        raise CheckFailure('You have to be in a voice channel')
    
    return True
     
async def same_channel(ctx):
    if ctx.author.voice.channel != ctx.me.voice.channel:
        raise CheckFailure('You have to be in the same channel')
    
    return True
    
async def me_in_channel(ctx):
    if not ctx.me.voice:
        raise CheckFailure(f'I am not in any channel, use "{BOT_PREFIX}join" to connect')        

    return True

@bot.event
async def on_ready():
    print(f'Logged in {bot.user.name}')

@bot.event
async def on_command_error(ctx, error):
    e = getattr(error, 'original', error)
    
    if isinstance(e, CheckFailure):
        await ctx.send(str(e))
    else:
        raise e

@bot.command(aliases=['j'])
@check(author_in_channel)
async def join(ctx):
    voice_channel = ctx.author.voice.channel
    if not ctx.voice_client:
        voice_client = await voice_channel.connect()
    else:
        await voice_client.move_to(voice_channel)
          
    await ctx.send(f'Successfully connected to {voice_channel}')

@bot.command(aliases=['l', 'exit'])
@check(author_in_channel)
@check(me_in_channel)
async def leave(ctx):
    voice_channel = ctx.author.voice.channel
    await ctx.voice_client.disconnect()
    await ctx.send(f'Successfully disconnected from {voice_channel}')

@bot.command(aliases=['p'])
@check(author_in_channel)
@check(me_in_channel)
@check(same_channel)
async def play(ctx, *args):        
    player = player_pool.get(ctx.guild)
    search_str = ' '.join(args)    
    search_result = y_client.search(search_str)
    track = search_result.tracks.results[0]    
    audio = Audio(track)
    await player.play(audio)
    await ctx.send(f'{audio.full_title} is playing now')

@bot.command()
@check(author_in_channel)
@check(me_in_channel)
@check(same_channel)
async def playlist(ctx, *args):    
    player = player_pool.get(ctx.guild)
    try:
        search_args = [str(args[0]), int(args[1])]
    except Exception as ex:
        raise(ex)        

    search_result = y_client.users_playlists_list(search_args[0])
    playlist = search_result[0]
    short_tracks = y_client.users_playlists(search_args[1], playlist.uid)[0].tracks
    tracks_id = [st.track_id for st in short_tracks]
    tracks = y_client.tracks(tracks_id)
    audio = [Audio(t) for t in tracks]

    await player.playlist(audio)
    await ctx.send(f'{len(tracks)} tracks added to the queue\n{audio[0].full_title} is playing now')

@bot.command()
@check(author_in_channel)
@check(me_in_channel)
@check(same_channel)
async def pause(ctx): 
    player = player_pool.get(ctx.guild)
    await player.pause()
    await ctx.send('Paused')

@bot.command()
@check(author_in_channel)
@check(me_in_channel)
@check(same_channel)
async def volume(ctx, *args):
    value = float(args[0])
    player = player_pool.get(ctx.guild)
    player.volume = value   
    await ctx.send(f'Changed the volume to {value}%')

@bot.command(aliases=['c', 'clr'])
@check(author_in_channel)
@check(me_in_channel)
@check(same_channel)
async def clear(ctx): 
    player = player_pool.get(ctx.guild)
    await player.clear()
    await ctx.send('The queue cleared')

@bot.command(aliases=['n', 'next'])
@check(author_in_channel)
@check(me_in_channel)
@check(same_channel)
async def skip(ctx):
    player = player_pool.get(ctx.guild)
    await player.next()
    await ctx.send('Next track')

@bot.command(aliases=['r'])
@check(author_in_channel)
@check(me_in_channel)
@check(same_channel)
async def resume(ctx):
    player = player_pool.get(ctx.guild)
    await player.resume()
    await ctx.send('Resumed')

@bot.command(aliases=['mix'])
@check(author_in_channel)
@check(me_in_channel)
@check(same_channel)
async def shuffle(ctx):
    player = player_pool.get(ctx.guild)
    await player.shuffle()
    queue, iter = await player.queue(10), count(1)
    titles = '\n'.join(f'{next(iter)}. {i.full_title}' for i in queue)
    await ctx.send('Tracks are mixed, here are the next 10 tracks:\n'+titles)

@bot.command()
@check(author_in_channel)
@check(me_in_channel)
@check(same_channel)
async def queue(ctx, amount: int = 10):
    player = player_pool.get(ctx.guild)
    queue, iter = await player.queue(amount), count(1)
    if not queue:
        await ctx.send('The queue is empty')

    titles = '\n'.join(f'{next(iter)}. {i.full_title}' for i in queue)
    await ctx.send(f'Next {len(queue)} tracks:\n'+titles)

if __name__ == "__main__":    
    bot.run(TOKEN)