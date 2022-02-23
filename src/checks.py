import discord
from discord.ext import commands,tasks
import time
import asyncio
class Checks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(seconds=1)
    async def loop(self): # check for expired memos in sql
        memos = self.cursor.execute("SELECT * FROM memos WHERE expires_second <= {}".format(time.time())).fetchall()
        for memo in memos:
            author = self.bot.get_user(memo[7])
            await author.send(f"Your memo ID `{memo[0]}` has expired.")
            self.cursor.execute("DELETE FROM memos WHERE id=?", (memo[0],))
    @commands.Cog.listener()
    async def on_ready(self):
        await asyncio.sleep(1)

        self.db = self.bot.db
        self.cursor = self.bot.cursor
        self.loop.start()

def setup(bot):
    bot.add_cog(Checks(bot))