import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
import sqlite3 as sqlite
import random as random

class voteKick(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.doubleVoteResponses = ["Don't try to fool me! You voted already.", "This is not how democracy works..", "Hold on, don't cast your vote twice.", "You really tried that? You voted already!", "No, you don't have more votes than others.."]
        self.banKickReasonResponses = ["Democracy has spoken", "You weren't wanted anymore..", "Everybody has to go..", "Farewell, banana.", "They are the senate!", "Personally.. I would do that too.", "Don't anger them again!"]

    @commands.command(name = "voteKick", pass_context = True, aliases = ["vK", "vk", "voteK", "vKick", "votek"])
    @has_permissions(kick_members = True)
    async def voteKick(self, ctx, name = None, count = 3):

        guild = ctx.guild.name.replace("'", "").replace(" ", "_") + "_votekick"
        conn = sqlite.connect("data/internal.db")

        if len(ctx.message.mentions) == 0:
            await ctx.send("***You didn't specify whome to start kick vote against!***")

        else:
            if len(conn.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{guild}'").fetchall()) == 0:
                conn.execute(f"CREATE TABLE IF NOT EXISTS {guild}('id' INTEGER PRIMARY KEY, 'kick_user' TEXT NOT NULL, 'kick_voters' TEXT NOT NULL, 'votes_current' INTEGER NOT NULL, 'votes_max' INTEGER NOT NULL)")
                conn.commit()
                print(f"Created votekick table in database for {guild[:len(guild) - 9]}")
                conn.execute(f"INSERT INTO {guild} VALUES(NULL, ?, ?, ?, ?)", (ctx.message.mentions[0].id, ctx.message.author.id, 1, count))
                conn.commit()
                kick_field = discord.Embed(colour = discord.Colour(0xFDED32))
                kick_field.add_field(name = f"Kicking vote in progress!", value = f"{ctx.message.mentions[0].mention} `1/{count}`", inline = True)
                await ctx.send(embed = kick_field)

            else:
                data = conn.execute(f"SELECT * FROM {guild} WHERE kick_user = '{ctx.message.mentions[0].id}'").fetchall()

                if len(data) == 0:
                    conn.execute(f"INSERT INTO {guild} VALUES(NULL, ?, ?, ?, ?)", (ctx.message.mentions[0].id, ctx.message.author.id, 1, count))
                    conn.commit()
                    kick_field = discord.Embed(colour = discord.Colour(0xFDED32))
                    kick_field.add_field(name = f"Kicking vote in progress!", value = f"{ctx.message.mentions[0].mention} `1/{count}`", inline = True)
                    await ctx.send(embed = kick_field)

                else:
                    data = data[0]
                    kick_user = data[1]
                    kick_voters = data[2].split("_")
                    votes_current = int(data[3])
                    votes_max = int(data[4])

                    if str(ctx.message.author.id) in kick_voters:
                        await ctx.send(f"***{self.doubleVoteResponses[random.randrange(len(self.doubleVoteResponses))]}***")
                    
                    else:
                        if votes_current >= (votes_max - 1):
                            await ctx.guild.get_member(int(kick_user)).kick(reason = f"{self.banKickReasonResponses[random.randrange(len(self.banKickReasonResponses))]}")
                            kick_field = discord.Embed(colour = discord.Colour(0xFDED32))
                            kick_field.add_field(name = f"You did it!", value = f"{ctx.message.mentions[0].mention} is no more.", inline = True)
                            await ctx.send(embed = kick_field)
                            conn.execute(f"DELETE FROM {guild} WHERE kick_user = '{kick_user}'")
                            conn.commit()

                        else:
                            votes_current += 1
                            kick_voters.append(ctx.author.id)
                            kick_voters = "_".join(map(str, kick_voters))
                            conn.execute(f"UPDATE {guild} SET votes_current = '{votes_current}', kick_voters = '{kick_voters}' WHERE kick_user = '{kick_user}'")
                            conn.commit()
                            kick_field = discord.Embed(colour = discord.Colour(0xFDED32))
                            kick_field.add_field(name = f"Kicking vote in progress!", value = f"{ctx.message.mentions[0].mention} `{votes_current}/{votes_max}`", inline = True)
                            await ctx.send(embed = kick_field)
        conn.close()
        
    @commands.command(name = "resetVoteKick", aliases = ["rVK", "rvk", "resetvK", "rKick", "rk", "rK", "resetvk"])
    async def resetVoteKick(self, ctx):

        guild = ctx.guild.name.replace("'", "").replace(" ", "_") + "_votekick"
        conn = sqlite.connect("data/internal.db")

        if len(conn.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{guild}'").fetchall()) == 0:
            await ctx.send("***There is no kick vote going on right now***")

        else:
            if len(ctx.message.mentions) == 0:
                if len(conn.execute(f"SELECT * FROM {guild}").fetchall()) > 0:
                    conn.execute(f"DELETE FROM {guild}")
                    conn.commit()
                    cancel_kick_field = discord.Embed(colour = discord.Colour(0xFDED32))
                    cancel_kick_field.add_field(name = f"Canceled all kick votes!", value = f"They are now all free!")
                    await ctx.send(embed = cancel_kick_field)
                else:
                    await ctx.send("***There is no kick vote against anybody on this server***")

            else:
                if len(conn.execute(f"SELECT * FROM {guild} WHERE kick_user = '{ctx.message.mentions[0].id}'").fetchall()) == 0:
                    await ctx.send("***There is no kick vote against this user***")
                else:
                    conn.execute(f"DELETE FROM {guild} WHERE kick_user = '{ctx.message.mentions[0].id}'")
                    cancel_kick_field = discord.Embed(colour = discord.Colour(0xFDED32))
                    cancel_kick_field.add_field(name = f"Canceled kick voting", value = f"{ctx.message.mentions[0].mention} is now free!")
                    await ctx.send(embed = cancel_kick_field)

        conn.close()

    @voteKick.error
    async def voteKickError(self, ctx, error):
        await ctx.send("***I don't have permission to do that!***")
        print(error)
    
        
def setup(bot):
    bot.add_cog(voteKick(bot))

def get_prefix(bot, message):
    conn = sqlite.connect("data/internal.db")
    try:
        return conn.execute(f"SELECT * FROM prefixes WHERE guild_id = {message.guild.id}").fetchall()[0][2]
    except:
        conn.execute(f"INSERT INTO prefixes VALUES(NULL, ?, ?)", (message.guild.id, "."))
        conn.commit()
        return conn.execute(f"SELECT * FROM prefixes WHERE guild_id = {message.guild.id}").fetchall()[0][2]

    conn.close()