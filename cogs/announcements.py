  
import asyncio

import discord
import youtube_dl
import sqlite3 as sqlite
from discord.ext import commands

class announcements(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def makeAnnouncements(self, ctx, name = None, title = "none", *fields):
        announcements_channels = [channel for channel in ctx.guild.text_channels if channel.is_news()] if name != None or name.lower() != "all" else [channel for channel in ctx.guild.text_channels if channel.is_news() and channel.lower() == name.lower()]
        announcement_field = discord.Embed(colour = discord.Colour(0xFDED32))
        announcement_field.set_author(name = "𝓐𝓷𝓷𝓸𝓾𝓷𝓬𝓮𝓶𝓮𝓷𝓽")
        if len(announcements_channels) == 0:
            announcement_field.add_field(name = f"{ctx.guild} doesn't have any news channels!", value = f"To make a new announcement you need to have at least one news channels", inline = False)
            await ctx.send(embed = announcement_field)
            await ctx.message.delete()
        else:
            if title.lower() != "none":
                announcement_field.title = title

            for i in range(0, len(fields), 2):
                announcement_field.add_field(name = f"{fields[i]}", value = f"{fields[i + 1]}", inline = False)

            for channel in announcements_channels:
                await channel.send(embed = announcement_field)
        
        await ctx.message.delete()


def setup(bot):
    bot.add_cog(announcements(bot))

def get_prefix(bot, message):
    conn = sqlite.connect("data/internal.db")
    try:
        return conn.execute(f"SELECT * FROM prefixes WHERE guild_id = {message.guild.id}").fetchall()[0][2]
    except:
        conn.execute(f"INSERT INTO prefixes VALUES(NULL, ?, ?)", (message.guild.id, "."))
        conn.commit()
        return conn.execute(f"SELECT * FROM prefixes WHERE guild_id = {message.guild.id}").fetchall()[0][2]

    conn.close()