from discord.ext.commands import Bot, DefaultHelpCommand

from .extended.errors import CheckFailure, PlayerError


class MusicBot(Bot):
    def __init__(self, command_prefix, help_command=None,
                 description=None, **options):

        if help_command is None:
            help_command = DefaultHelpCommand()

        super().__init__(command_prefix, help_command=help_command,
                         description=description, **options)

    async def on_ready(self):
        print(f'Logged in {self.user.name}')

    async def on_command_error(self, ctx, error):
        e = getattr(error, 'original', error)

        if isinstance(e, (CheckFailure, PlayerError)):
            await ctx.send(e)
        else:
            raise e
