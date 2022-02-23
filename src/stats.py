import discord
from discord.ext import commands
import psutil

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='stats')
    async def stats(self, ctx):
        """
        Shows the bot's stats.
        """
        embed = discord.Embed(
            title="Stats",
            description="",
            color=0x00ff00
        )

        embed.add_field(
            name="CPU usage",
            value=f"{psutil.cpu_percent()}%",
            inline=True
        )

        embed.add_field(
            name="RAM usage",
            value=f"{psutil.virtual_memory().percent}%",
            inline=True
        )

        embed.add_field(
            name="Uptime",
            value=f"{round(self.bot.uptime)} seconds",
            inline=True
        )

    @commands.command(name='ping')
    async def ping(self, ctx):
        """
        Shows the bot's latency.
        """
        await ctx.send(f"Pong! {round(self.bot.latency * 1000)}ms")

def setup(bot):
    bot.add_cog(Stats(bot))