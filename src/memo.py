import discord
from discord.ext import commands
import base64
import time
import json
import string
import random
import datetime
import mimetypes
class Confirm(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message('Confirming', ephemeral=True)
        self.value = True
        self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message('Cancelling', ephemeral=True)
        self.value = False
        self.stop()

class Memo_Pusher(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cursor = bot.cursor
        self.db = bot.db

    @commands.group(name='memo_push', aliases=['mp'])
    async def memo_push(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid Command')

    def parse_time(self, t):
        try:
            if t.isdigit():
                return int(t)
            elif t.endswith('s'):
                return int(t[:-1])
            elif t.endswith('m'):
                return int(t[:-1]) * 60
            elif t.endswith('h'):
                return int(t[:-1]) * 60 * 60
            elif t.endswith('d'):
                return int(t[:-1]) * 60 * 60 * 24
            elif t.endswith('w'):
                return int(t[:-1]) * 60 * 60 * 24 * 7
            elif t.endswith('y'):
                return int(t[:-1]) * 60 * 60 * 24 * 7 * 365
            else:
                return -1
        except:
            # int
            return t


    @memo_push.command(name='add', aliases=['a'])
    async def add(self, ctx, end:int=-1,password:str='', memo:str= None):
        """Add a memo"""
        await ctx.message.delete()
        end = self.parse_time(end)
        encoded_memo_attachment = json.dumps({'files': [base64.b64encode(await file.read()).decode('utf-8') for file in ctx.message.attachments]})
        memo_created = int(time.time())
        view = Confirm()
        embed = discord.Embed(title="You are going to add a memo that may contain infos that can be easily compromised.\nAre you sure you want to continue?", color=0x00ff00)
        embed.add_field(name="Memo", value=memo)
        embed.add_field(name="End", value=datetime.datetime.fromtimestamp(memo_created + end).strftime('%Y-%m-%d %H:%M:%S'))
        embed.add_field(name="Password", value=password)
        embed.add_field(name="Attachment", value=len(ctx.message.attachments))
        embed.set_footer(text="This will be deleted in {} seconds or at {}".format(end, datetime.datetime.fromtimestamp(memo_created + end).strftime('%Y-%m-%d %H:%M:%S')))
        await ctx.author.send(embed=embed, view=view)
        await view.wait()
        if view.value:
            id = ''.join(random.sample(string.ascii_letters+string.digits, 20))
            self.cursor.execute(f"INSERT INTO memos (id, text_, day, when_second, expires_second, expire_day, files, author_id, password) VALUES ({id}, '{memo}', {str(datetime.datetime.now()).replace('-','/')}, {memo_created}, {memo_created + end}, {str(datetime.datetime.fromtimestamp(memo_created + end)).replace('-','/')}, '{encoded_memo_attachment}', {ctx.author.id}, '{password}')")
            self.db.commit()
            await ctx.author.send(embed=discord.Embed(
                title="Memo added",
                description="Your memo has been added.\nYou can view it with `!memo view {}`".format(id),
            ))
        else:
            await ctx.author.send(embed=discord.Embed(
                title="Memo not added",
                description="Your memo has not been added.",
            ))
    
    @memo_push.command(name='edit', aliases=['e'])
    async def edit(self, ctx, end:int=-1, password:str='',*,memo):
        """Edit a memo"""
        await ctx.message.delete()
        if end == -1:
            await ctx.author.send(embed=discord.Embed(
                title="Using default expiration",
                description="You did not specify an expiration time.\nThe default expiration time is your memo expire time or forever"
            ))
        if password == '':
            await ctx.author.send(embed=discord.Embed(
                title="Using default password",
                description="You did not specify a password.\nThe default password is your memo password or none"
            ))
        if ctx.author.id != int(self.cursor.execute(f"SELECT author_id FROM memos WHERE id = '{ctx.message.content.split(' ')[1]}'").fetchone()[0]):
            await ctx.author.send(embed=discord.Embed(
                title="You are not the author of this memo",
                description="You are not the author of this memo"
            ))
            return
        end = self.parse_time(end)
        encoded_memo_attachment = json.dumps({'files': [base64.b64encode(await file.read()).decode('utf-8') for file in ctx.message.attachments]})
        memo_created = int(time.time())
        view = Confirm()
        embed = discord.Embed(title="You are going to edit a memo that may contain infos that can be easily compromised.\nAre you sure you want to continue?", color=0x00ff00)
        embed.add_field(name="Memo", value=memo)
        embed.add_field(name="End", value=datetime.datetime.fromtimestamp(memo_created + end).strftime('%Y-%m-%d %H:%M:%S'))
        embed.add_field(name="Password", value=password)
        embed.add_field(name="Attachment", value=len(ctx.message.attachments))
        embed.set_footer(text="This will be deleted in {} seconds or at {}".format(end, datetime.datetime.fromtimestamp(memo_created + end).strftime('%Y-%m-%d %H:%M:%S')))
        await ctx.author.send(embed=embed, view=view)
        await view.wait()
        if view.value:
            self.cursor.execute(f"UPDATE memos SET text_ = '{memo}', day = {str(datetime.datetime.now()).replace('-','/')}, when_second = {memo_created}, expires_second = {memo_created + end}, expire_day = {str(datetime.datetime.fromtimestamp(memo_created + end)).replace('-','/')}, files = '{encoded_memo_attachment}', password = '{password}' WHERE author_id = {ctx.author.id}")
            self.db.commit()
            await ctx.author.send(embed=discord.Embed(
                title="Memo edited",
                description="Your memo has been edited.\nYou can view it with `!memo view {}`".format(id),
            ))
        else:
            await ctx.author.send(embed=discord.Embed(
                title="Memo not edited",
                description="Your memo has not been edited.",
            ))
    
    @memo_push.command(name='delete', aliases=['d'])
    async def delete(self, ctx, id:str=None):
        """Delete a memo"""
        await ctx.message.delete()
        if id is None:
            await ctx.author.send(embed=discord.Embed(
                title="No memo id",
                description="You did not specify a memo id"
            ))
            return
        if ctx.author.id != int(self.cursor.execute(f"SELECT author_id FROM memos WHERE id = '{id}'").fetchone()[0]):
            await ctx.author.send(embed=discord.Embed(
                title="You are not the author of this memo",
                description="You are not the author of this memo"
            ))
            return
        view = Confirm()
        embed = discord.Embed(title="You are going to delete a memo.\nAre you sure you want to continue?", color=0x00ff00)
        embed.add_field(name="Memo id", value=id)
        await ctx.author.send(embed=embed, view=view)
        await view.wait()
        if view.value:
            self.cursor.execute(f"DELETE FROM memos WHERE id = '{id}'")
            self.db.commit()
            await ctx.author.send(embed=discord.Embed(
                title="Memo deleted",
                description="Your memo has been deleted.",
            ))
        else:
            await ctx.author.send(embed=discord.Embed(
                title="Memo not deleted",
                description="Your memo has not been deleted.",
            ))
        
        

        
class Memo_Getter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cursor = bot.cursor
        self.db = bot.db
    
    @commands.group(name='memo_get', aliases=['mg'])
    async def memo_get(self, ctx):
        """Get a memo"""
        if ctx.invoked_subcommand is None:
            await ctx.send(embed=discord.Embed(
                title="Memo getter",
                description="You did not specify a command.\nUse `!memo_get help` to see all commands"
            ))
    
    @memo_get.command(name='help', aliases=['h'])
    async def help(self, ctx):
        """Get help for memo getter"""
        await ctx.send(embed=discord.Embed(
            title="Memo getter help",
            description="Use `!memo_get [command]` to get help for a command"
        ))
    
    @memo_get.command(name='list', aliases=['l'])
    async def list(self, ctx):
        """Get a list of all your memos"""
        await ctx.message.delete()
        memos = self.cursor.execute(f"SELECT id, text_, when_second, expires_second, expire_day, password FROM memos WHERE author_id = {ctx.author.id}").fetchall()
        if len(memos) == 0:
            await ctx.author.send(embed=discord.Embed(
                title="No memos",
                description="You have no memos"
            ))
            return
        embed = discord.Embed(title="Your memos", description="")
        for memo in memos:
            if memo[3] == -1:
                end = "Forever"
            else:
                end = datetime.datetime.fromtimestamp(memo[3]).strftime('%Y-%m-%d %H:%M:%S')
            embed.add_field(name=f"{memo[0]} - {memo[1]}", value=f"{datetime.datetime.fromtimestamp(memo[2]).strftime('%Y-%m-%d %H:%M:%S')} - {end} - {memo[4]}")
        await ctx.author.send(embed=embed)
    
    @memo_get.command(name='view', aliases=['v'])
    async def view(self, ctx, id:str=None):
        """View a memo"""
        await ctx.message.delete()
        if id is None:
            await ctx.author.send(embed=discord.Embed(
                title="No memo id",
                description="You did not specify a memo id"
            ))
            return
        memo = self.cursor.execute(f"SELECT text_, when_second, expires_second, expire_day, password, files FROM memos WHERE id = '{id}'").fetchone()
        if memo is None:
            await ctx.author.send(embed=discord.Embed(
                title="No memo",
                description="You did not specify a valid memo id"
            ))
            return
        if memo[4] != "":
            if ctx.author.id != int(self.cursor.execute(f"SELECT author_id FROM memos WHERE id = '{id}'").fetchone()[0]):
                await ctx.author.send(embed=discord.Embed(
                    title="You are not the author of this memo",
                    description="You are not the author of this memo"
                ))
                return
        else:
            await ctx.author.send("Please enter the password for this memo")
            password = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
            if password.content != memo[4]:
                await ctx.author.send(embed=discord.Embed(
                    title="Wrong password",
                    description="You entered the wrong password"
                ))
                return
        if memo[3] == -1:
            end = "Forever"
        else:
            end = datetime.datetime.fromtimestamp(memo[3]).strftime('%Y-%m-%d %H:%M:%S')
        embed = discord.Embed(title="Memo", description="")
        embed.add_field(name="Memo", value=memo[0])
        embed.add_field(name="Created", value=datetime.datetime.fromtimestamp(memo[1]).strftime('%Y-%m-%d %H:%M:%S'))
        embed.add_field(name="End", value=end)
        embed.add_field(name="Password", value=memo[4])
        if memo[5] != "":
            embed.add_field(name="Attachment", value=len(memo[5].split(",")))
        files = []
        for file in json.loads(memo[5])["files"].items():
            id = ''.join(random.choice(string.ascii_uppercase + string.digits,10))
            type = mime.guess_type(base64.b64decode(file))
            with open(f"/temp/{id}.{type[0].split('/')}", "wb") as f:
                fp.write(base64.b64decode(file))
            files.append(f"/temp/{id}.{type[0].split('/')}")
        if len(files) != 0:
            embed.add_field(name="Files", value=len(files))
        await ctx.author.send(
            embed=embed,
            files=files
        )
        for file in files:
            os.remove(file)

    @memo_get.command(name='stats', aliases=['s'])
    async def stats(self, ctx):
        """Get stats about your memos"""
        await ctx.message.delete()
        amount_of_memos = self.cursor.execute(f"SELECT COUNT(*) FROM memos WHERE author_id = {ctx.author.id}").fetchone()[0]
        amount_of_expired_memos = self.cursor.execute(f"SELECT COUNT(*) FROM memos WHERE author_id = {ctx.author.id} AND expires_second != -1 AND expires_second < {int(time.time())}").fetchone()[0]
        amount_of_expired_memos_today = self.cursor.execute(f"SELECT COUNT(*) FROM memos WHERE author_id = {ctx.author.id} AND expires_second != -1 AND expires_second < {int(time.time())} AND expire_day = {int(time.strftime('%d'))}").fetchone()[0]
        amount_of_characters_in_each_memos = self.cursor.execute(f"SELECT SUM(LENGTH(text_)) FROM memos WHERE author_id = {ctx.author.id}").fetchone()[0]
        embed = discord.Embed(title="Memo stats", description="")
        embed.add_field(name="Amount of memos", value=amount_of_memos)
        embed.add_field(name="Amount of expired memos", value=amount_of_expired_memos)
        embed.add_field(name="Amount of expired memos today", value=amount_of_expired_memos_today)
        embed.add_field(name="Amount of characters in each memos", value=amount_of_characters_in_each_memos)
        await ctx.author.send(embed=embed)
        
    
def setup(bpt):
    bpt.add_cog(Memo_Pusher(bpt))
    bpt.add_cog(Memo_Getter(bpt))