from discord.ext.commands.errors import *


class CheckAllFailure(CheckFailure):
    pass


class MissingInChannel(CheckFailure):
    pass


class ExistingInAnotherChannel(CheckFailure):
    pass


class SameChannelsError(CheckFailure):
    pass


class PlayerError(CommandError):
    def __init__(self, message=None):

        if message is None:
            super().__init__('Something wrong with player')
        else:
            super().__init__(message)


class PlayerInvalidState(PlayerError):
    pass


class PlayerInvalidVolume(PlayerError):
    pass


class PlayerQueueEmpty(PlayerError):
    def __init__(self, message=None):

        if message is None:
            super().__init__('No music in the queue')
        else:
            super().__init__(message)
