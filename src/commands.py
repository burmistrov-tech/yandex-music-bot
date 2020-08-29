import itertools

from yandex_music import Client
from discord.ext.commands import Bot, Cog, command

from .audio import Audio
from .player import PlayerPool
from .extended.checks import *

class BotCommands(Cog):
    def __init__(self, bot: Bot, yandex_client: Client = None):
        self.bot = bot

        if yandex_client is None:
            yandex_client = Client()

        self.yandex_client = yandex_client
        self.player_pool = PlayerPool(self.bot)
        
    @command(aliases=['j'])
    @author_in_channel()
    async def join(self, ctx):
        voice_channel = ctx.author.voice.channel
        if not ctx.voice_client:
            voice_client = await voice_channel.connect()
        else:
            await voice_client.move_to(voice_channel)
            
        await ctx.send(f'Successfully connected to {voice_channel}')

    @command(aliases=['l', 'exit'])
    @check_all(author_in_channel(), bot_in_channel())
    async def leave(self, ctx):
        voice_channel = ctx.author.voice.channel
        await ctx.voice_client.disconnect()
        await ctx.send(f'Successfully disconnected from {voice_channel}')

    @command()
    @check_all(author_in_channel(), bot_in_channel(), in_same_channel())
    async def volume(self, ctx, *args):
        value = float(args[0])
        player = self.player_pool.get(ctx.guild)
        player.volume = value   
        await ctx.send(f'Changed the volume to {value}%')

    @command(aliases=['p'])
    @check_all(author_in_channel(), bot_in_channel(), in_same_channel())
    async def play(self, ctx, *args):        
        player = self.player_pool.get(ctx.guild)
        search_str = ' '.join(args)    
        search_result = self.yandex_client.search(search_str, type_='track')
        track = search_result.tracks.results[0]    
        audio = Audio(track)
        await player.play(audio)
        await ctx.send(f'{audio.full_title} is playing now')

    @command()
    @check_all(author_in_channel(), bot_in_channel(), in_same_channel())
    async def playlist(self, ctx, *args):    
        player = self.player_pool.get(ctx.guild)
        try:
            search_args = [str(args[0]), int(args[1])]
        except Exception as ex:
            raise(ex)        

        search_result = self.yandex_client.users_playlists_list(search_args[0])
        playlist = search_result[0]
        short_tracks = self.yandex_client.users_playlists(search_args[1], playlist.uid)[0].tracks
        tracks_id = [st.track_id for st in short_tracks]
        tracks = self.yandex_client.tracks(tracks_id)
        audio = [Audio(t) for t in tracks]

        await player.playlist(audio)
        await ctx.send(f'{len(tracks)} tracks added to the queue\n{audio[0].full_title} is playing now')

    @command()
    @check_all(author_in_channel(), bot_in_channel(), in_same_channel())
    async def pause(self, ctx): 
        player = self.player_pool.get(ctx.guild)
        await player.pause()
        await ctx.send('Paused')

    @command(aliases=['r'])
    @check_all(author_in_channel(), bot_in_channel(), in_same_channel())
    async def resume(self, ctx):
        player = self.player_pool.get(ctx.guild)
        await player.resume()
        await ctx.send('Resumed')

    @command()
    async def stop(self, ctx):
        player = self.player_pool.get(ctx.guild)
        await player.stop()
        await ctx.send('Stopped')

    @command(aliases=['n', 'next'])
    @check_all(author_in_channel(), bot_in_channel(), in_same_channel())
    async def skip(self, ctx):
        player = self.player_pool.get(ctx.guild)
        await player.next()
        await ctx.send('Next track')

    @command(aliases=['mix'])
    @check_all(author_in_channel(), bot_in_channel(), in_same_channel())
    async def shuffle(self, ctx):
        player = self.player_pool.get(ctx.guild)
        await player.shuffle()
        queue, iter = await player.queue(10), itertools.count(1)
        titles = '\n'.join(f'{next(iter)}. {i.full_title}' for i in queue)
        await ctx.send('Tracks are mixed, here are the next 10 tracks:\n'+titles)

    @command()
    @check_all(author_in_channel(), bot_in_channel(), in_same_channel())
    async def queue(self, ctx, amount: int = 10):
        player = self.player_pool.get(ctx.guild)
        queue, iter = await player.queue(amount), itertools.count(1)
        if not queue:
            await ctx.send('The queue is empty')

        titles = '\n'.join(f'{next(iter)}. {i.full_title}' for i in queue)
        await ctx.send(f'Next {len(queue)} tracks:\n'+titles)

    @command(aliases=['c', 'clr'])
    @check_all(author_in_channel(), bot_in_channel(), in_same_channel())
    async def clear(self, ctx): 
        player = self.player_pool.get(ctx.guild)
        await player.clear()
        await ctx.send('The queue cleared')