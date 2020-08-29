from discord.ext.commands.errors import *

class CheckAllFailure(CheckFailure):
    pass

class MissingInChannel(CheckFailure):
    pass

class SameChannelsError(CheckFailure):
    pass

