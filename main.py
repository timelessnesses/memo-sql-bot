import discord
from discord.ext import commands
import sqlite3
import asyncio
from dotenv import load_dotenv
load_dotenv()
import os

bot = commands.Bot(command_prefix='!')

bot.remove_command('help')

bot.db = sqlite3.connect('memo.db')
bot.cursor = bot.db.cursor()
@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    bot.cursor.executescript(open('starts.sql','r',encoding='utf-8').read())
    bot.db.commit()

    print("Created Database")

for filename in os.listdir('./src'):
    if filename.endswith('.py'):
        bot.load_extension(f'src.{filename[:-3]}')

try:
    bot.run(os.getenv('Memo_Token'))
except KeyboardInterrupt:
    print("\nRecieved Keyboard Interrupt..\nClosing Database",end="\r")
    bot.db.close()
    print("Recieved Keyboard Interrupt..\nClosed Database",end="\r")
    print("\nExiting..")
    exit()
except Exception as e:
    print(e)
    print("\nExiting..")
    exit()
except:
    print("\nExiting..")
    exit()
    