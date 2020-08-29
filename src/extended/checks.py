from discord.ext.commands import check, check_any

from .errors import CheckAllFailure, MissingInChannel, SameChannelsError

def check_all(*checks):
    unwrapped = []
    for wrapped in checks:
        try:
            pred = wrapped.predicate
        except AttributeError:
            raise TypeError('%r must be wrapped by commands.check decorator' % wrapped) from None
        else:
            unwrapped.append(pred)

    async def predicate(ctx):
        for func in unwrapped:
            if not await func(ctx):
                raise CheckAllFailure(f'The check function {func.__name__} failed.')                      
        # if we're here, all checks passed
        return True
    return check(predicate) 

def author_in_channel():
    async def predicate(ctx):
        if ctx.author.voice is None:
            raise MissingInChannel('You have to be in the same channel')

        return True
    return check(predicate)

def bot_in_channel():
    async def predicate(ctx):
        if ctx.me.voice is None:
            raise MissingInChannel(f'Bot in any channel, use "{ctx.bot.command_prefix}join" to connect')

        return True
    return check(predicate)

def in_same_channel():
    async def predicate(ctx):
        if ctx.author.voice.channel != ctx.me.voice.channel:
            raise SameChannelsError('You have to be in the same channel')

        return True
    return check(predicate)