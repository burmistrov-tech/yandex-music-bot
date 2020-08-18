import json
import logging
from audio import Audio
from yandex_music import Client
from discord.ext.commands import Bot, check, CheckFailure
from player import Player, PlayerPool

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
        raise CheckFailure('You are not in any channel')
    
    return True
     
async def same_channel(ctx):
    if ctx.author.voice.channel != ctx.me.voice.channel:
        raise CheckFailure('You have to be in the same channel')
    
    return True
    
async def me_in_channel(ctx):
    if not ctx.me.voice:
        raise CheckFailure(f'I am not in any channel, use {BOT_PREFIX}join to connect')        

    return True

@bot.event
async def on_ready():
    print('Logged in ' + bot.user.name + '\n')

@bot.event
async def on_command_error(ctx, error):
    e = getattr(error, 'original', error)
    
    if isinstance(e, CheckFailure):
        await ctx.send(str(e))
    else:
        raise e

@bot.command(aliases=['j', 'jo'])
@check(author_in_channel)
async def join(ctx):
    voice_channel = ctx.author.voice.channel
    if not ctx.voice_client:
        voice_client = await voice_channel.connect()
    else:
        await voice_client.move_to(voice_channel)
          
    await ctx.send(f'{bot.user.name} has connected to {voice_channel}')

@bot.command(aliases=['l', 'lv'])
@check(author_in_channel)
@check(me_in_channel)
async def leave(ctx):
    voice_channel = ctx.author.voice.channel
    await ctx.voice_client.disconnect()
    await ctx.send(f'{bot.user.name} has left {voice_channel}')

@bot.command(aliases=['p', 'pl'])
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
    await ctx.send('Downloading tracks')

    short_tracks = y_client.users_playlists(search_args[1], playlist.uid)[0].tracks
    tracks_id = [st.track_id for st in short_tracks]
    tracks = y_client.tracks(tracks_id)
    audio = [Audio(t) for t in tracks]

    await player.playlist(audio)

@bot.command(aliases=['pau', 'ps'])
@check(author_in_channel)
@check(me_in_channel)
@check(same_channel)
async def pause(ctx): 
    player = player_pool.get(ctx.guild)
    await player.pause()
    await ctx.send('Music has stopped')

@bot.command()
@check(author_in_channel)
@check(me_in_channel)
@check(same_channel)
async def volume(ctx, *args):
    value = float(args[0])
    player = player_pool.get(ctx.guild)
    player.volume = value
    await ctx.send(f'Changed volume to {value}%')

@bot.command(aliases=['clr'])
@check(author_in_channel)
@check(me_in_channel)
@check(same_channel)
async def clear(ctx): 
    player = player_pool.get(ctx.guild)
    await player.clear()
    await ctx.send('Queue is clear')

@bot.command(aliases=['n', 'skip'])
@check(author_in_channel)
@check(me_in_channel)
@check(same_channel)
async def next(ctx):
    player = player_pool.get(ctx.guild)
    await player.next()
    await ctx.send('Next track')

@bot.command(aliases=['r', 'rsm'])
@check(author_in_channel)
@check(me_in_channel)
@check(same_channel)
async def resume(ctx):
    player = player_pool.get(ctx.guild)
    await player.resume()
    await ctx.send('Music has resumed')

@bot.command(alaliases=['mix'])
@check(author_in_channel)
@check(me_in_channel)
@check(same_channel)
async def shuffle(ctx):
    player = player_pool.get(ctx.guild)
    await player.shuffle()
    audio = await player.queue()
    titles = '\n'.join(a.full_title for a in audio)
    await ctx.send('Tracks are mixed, here are the next 10 tracks:\n'+titles)

if __name__ == "__main__":    
    bot.run(TOKEN)