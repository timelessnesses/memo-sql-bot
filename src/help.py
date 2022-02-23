import discord
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='help')
    async def help(self, ctx, *, command=None):
        if command is None:
            commands_ = self.bot.commands
            embed = discord.Embed(title='Help', description='List of commands', color=0x00ff00)
            for command in commands_:
                embed.add_field(name=command.name, value=command.help, inline=False) 
        else:
            command = self.bot.get_command(command)
            if command is None:
                await ctx.send(f'Command {command} not found.')
            else:
                embed = discord.Embed(title=command.name, description=command.help, color=0x00ff00)
        embed.set_footer(text="Made by: @Unpredictable#9773\nConsider star this repo on GitHub: https://github.com/timelessnesses/memo-sql-bot")
        await ctx.send(embed=embed)
    
def setup(bot):
    bot.add_cog(Help(bot))
