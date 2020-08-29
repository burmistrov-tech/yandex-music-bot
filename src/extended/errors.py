from discord.ext.commands.errors import *

class CheckAllFailure(CheckFailure):
    pass

class MissingInChannel(CheckFailure):
    pass

class SameChannelsError(CheckFailure):
    pass

class PlayerError(CommandError):
    def __init__(self, message, *args):

        if message is None:
            super().__init__('Something wrong with player', args)
        else:
            super().__init__(message, args)

class PlayerInvalidState(PlayerError):
    pass

class PlayerInvalidVolume(PlayerError):
    pass

class PlayerQueueEmpty(PlayerError):
    def __init__(self, message = None, *args):

        if message is None:            
            super().__init__('No music in the queue', args)
        else:
            super().__init__(message, args)
