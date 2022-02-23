import discord
from discord.ext import commands
import io
import traceback

class Error_Handling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return

        ignored = (commands.CommandNotFound, commands.UserInputError)
        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return

        elif isinstance(error, commands.DisabledCommand):
            return await ctx.send(f'{ctx.command} has been disabled.')

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
            except:
                pass

        elif isinstance(error, commands.BadArgument):
            if ctx.command.qualified_name == 'tag list':
                return await ctx.send('I could not find that member. Please try again.')

        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f'{ctx.command} requires the argument {error.param}.')

        elif isinstance(error, commands.BotMissingPermissions):
            return await ctx.send(f'I do not have the permissions to run {ctx.command}.')

        elif isinstance(error, commands.CheckFailure):
            return await ctx.send('You do not have permission to use this command.')

        elif isinstance(error, commands.CommandOnCooldown):
            return await ctx.send(f'This command is on cooldown. Try again in {error.retry_after:.2f}s.')

        else:
            error = ''.join(traceback.TracebackException.from_exception(error).format())
            file = io.StringIO(error)
            await ctx.send(file=discord.File(file, filename='error.txt'))

def setup(bot):
    bot.add_cog(Error_Handling(bot))