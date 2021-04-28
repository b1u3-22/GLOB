import discord
from discord import Client
from discord.ext import commands
from discord.utils import get
from discord.ext.commands import has_permissions
import sqlite3 as sqlite
import random as random

class nicknameManagment(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name = "changeNickname", aliases = ["cn", "cNick"])
    async def changeNickname(self, ctx, nickname = ""):
        nickname_field = discord.Embed(colour = discord.Colour(0xFDED32))
        nickname_field.set_author(name = "𝓝𝓲𝓬𝓴𝓷𝓪𝓶𝓮 𝓶𝓪𝓷𝓪𝓰𝓶𝓮𝓷𝓽")
        if nickname.lower().startswith("<@"):
            nickname = ""

        if len(ctx.message.mentions) == 0:
            nickname_field.add_field(name= "You have to mention users!", value = f"If you want to delete or add nicknames to user, you have to mention them, {ctx.author.mention}")
            await ctx.send(embed = nickname_field)
        else:
            for member in ctx.message.mentions:
                await member.edit(nick = nickname)
                if nickname != "":
                    nickname_field.add_field(name= f"User re-nicknamed!", value = f"{member.name} is now known as {member.mention}")
                else:
                    nickname_field.add_field(name= f"Member has beed stripped of his nickname", value = f"Was it something stupid or you just don't like {member.mention}?")

            await ctx.send(embed = nickname_field)
        
def setup(bot):
    bot.add_cog(nicknameManagment(bot))

def get_prefix(bot, message):
    conn = sqlite.connect("data/internal.db")
    try:
        return conn.execute(f"SELECT * FROM prefixes WHERE guild_id = {message.guild.id}").fetchall()[0][2]
    except:
        conn.execute(f"INSERT INTO prefixes VALUES(NULL, ?, ?)", (message.guild.id, "."))
        conn.commit()
        return conn.execute(f"SELECT * FROM prefixes WHERE guild_id = {message.guild.id}").fetchall()[0][2]

    conn.close()