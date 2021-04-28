import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
import sqlite3 as sqlite
import random as random
import sys

class citations(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.whatDidYouSayResponses = ["Proudly by: ", "Shamefully by: ", "Dumbly by: ", "Ironicaly: ", "With big smile on their face by: ", "Crying "]

    @commands.command(name = "writeThatDown", aliases = ["wtd", "CiteIt", "citeit", "writeD", "wd"])
    async def writeThatDown(self, ctx, text, author = None, name = None):

        conn = sqlite.connect("data/internal.db")
        text = text.replace(" ", "_").replace(",", "_").replace("'", "___")
        guild = ctx.guild.name.replace("'", "").replace(" ", "_") + "_citations"

        if name != None:
            name = name.replace(" ", "_").replace(",", "_").replace("'", "___").lower()

        if len(conn.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{guild}'").fetchall()) == 0:
            conn.execute(f"CREATE TABLE IF NOT EXISTS {guild}('id' INTEGER PRIMARY KEY, 'text' TEXT NOT NULL, 'author' TEXT NOT NULL, 'name' TEXT)")
            conn.commit()
            print(f"Created citations table in database for {guild[:len(guild) - 10]}")

        conn.execute(f"INSERT INTO {guild} VALUES(NULL, ?, ?, ?)", (text, ctx.message.mentions[0].id, name))
        conn.commit()

        if ctx.author.nick != None:
            await ctx.send(f"Got it, {ctx.author.nick}!")
        else:
            await ctx.send(f"Got it, {ctx.message.author.name}!")

        conn.close()

    @commands.command(name = "whatDidYouSay", aliases = ["wdys", "Cite", "cite", "what", "ws"]) 
    async def whatDidYouSay(self, ctx, author = None, name = None):

        conn = sqlite.connect("data/internal.db")
        guild = ctx.guild.name.replace("'", "").replace(" ", "_") + "_citations"

        if name != None:
            name = name.replace(" ", "_").replace(",", "_").replace("'", "___").lower()

        if len(conn.execute(f"SELECT name FROM sqlite_master WHERE type = 'table' AND name = '{guild}'").fetchall()) != 0:
            if len(ctx.message.mentions) > 0:

                if name != None:
                    data = conn.execute(f"SELECT * FROM {guild} WHERE author='{ctx.message.mentions[0].id}' AND name = '{name}'").fetchall()

                    if len(data) == 0:
                        await ctx.send(f"User {ctx.message.mentions[0].mention} didn't say anything funny or nobody saved that quote under a specific name. Don't worry, you can save t using `{get_prefix(self.bot, ctx.message)}writeThatDown`")

                else:
                    data = conn.execute(f"SELECT * FROM {guild} WHERE author='{ctx.message.mentions[0].id}'").fetchall()

                    if len(data) == 0:
                        await ctx.send(f"User {ctx.message.mentions[0].mention} is probably really boring")
            
            else: 
                data = conn.execute(f"SELECT * FROM {guild}").fetchall()

            quote = random.randrange(len(data))
            text = data[quote][1].replace("___", "'").replace("__", ", ").replace("_", " ")
            author = data[quote][2]

            whatDidYouSay_field = ping_field = discord.Embed(colour = discord.Colour(0xFDED32))
            whatDidYouSay_field.add_field(name = f"'{text}'", value = f"{self.whatDidYouSayResponses[random.randrange(len(self.whatDidYouSayResponses))]}{self.bot.get_user(int(author)).mention}", inline = False)

            await ctx.send(embed = whatDidYouSay_field)
        else:
            await ctx.send(f"***You have to save some life changing messages first!***")

        conn.close()


def setup(bot):
    bot.add_cog(citations(bot))

def get_prefix(bot, message):
    conn = sqlite.connect("data/internal.db")
    try:
        return conn.execute(f"SELECT * FROM prefixes WHERE guild_id = {message.guild.id}").fetchall()[0][2]
    except:
        conn.execute(f"INSERT INTO prefixes VALUES(NULL, ?, ?)", (message.guild.id, "."))
        conn.commit()
        return conn.execute(f"SELECT * FROM prefixes WHERE guild_id = {message.guild.id}").fetchall()[0][2]

    conn.close()