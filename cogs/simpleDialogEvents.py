import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
import sqlite3 as sqlite
import random as random

class simpleDialogEvents(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.apeResponses = ["What did you say you lil punk?", "I can do more calculation a second than you in your whole life!", "If I'm an ape, then you are a banana!"]

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author == self.bot.user:
            return

        if "ape" in message.content.lower():
            await message.channel.send(f"***{self.apeResponses[random.randrange(len(self.apeResponses))]}***")
        elif "globprefix" in message.content.lower():
            try: 
                await message.channel.send(f"My current prefix on this server is ***{get_prefix(self.bot, message)}***")
            except:
                await message.channel.send(f"Sorry, it seems my prefix is broken on this server. Try to remove me and add me again")

def setup(bot):
    bot.add_cog(simpleDialogEvents(bot))

def get_prefix(bot, message):
    conn = sqlite.connect("internal.db")
    try:
        return conn.execute(f"SELECT * FROM prefixes WHERE guild_id = {message.guild.id}").fetchall()[0][2]
    except:
        conn.execute(f"INSERT INTO prefixes VALUES(NULL, ?, ?)", (message.guild.id, "."))
        conn.commit()
        return conn.execute(f"SELECT * FROM prefixes WHERE guild_id = {message.guild.id}").fetchall()[0][2]

    conn.close()