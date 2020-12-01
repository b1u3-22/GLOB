import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
import sqlite3 as sqlite
import random as random

class voteBan(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.doubleVoteResponses = ["Don't try to fool me! You voted already.", "This is not how democracy works..", "Hold on, don't cast your vote twice.", "You really tried that? You voted already!", "No, you don't have more votes than others.."]
        self.banKickReasonResponses = ["Democracy has spoken", "You weren't wanted anymore..", "Everybody has to go..", "Farewell, banana.", "They are the senate!", "Personally.. I would do that too.", "Don't anger them again!"]

    @commands.command(name = "voteBan", aliases = ["vB", "vb", "voteB", "vBan"], pass_context = True)
    @has_permissions(ban_members = True)
    async def voteBan(self, ctx, name = None, count = 5):

        conn = sqlite.connect("internal.db")
        guild = ctx.guild.name.replace("'", "").replace(" ", "_") + "_voteban"

        if len(ctx.message.mentions) == 0:
            await ctx.send("***You didn't specify whome to start kick vote against!***")

        else:
            if len(conn.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{guild}'").fetchall()) == 0:
                conn.execute(f"CREATE TABLE IF NOT EXISTS {guild}('id' INTEGER PRIMARY KEY, 'ban_user' TEXT NOT NULL, 'ban_voters' TEXT NOT NULL, 'votes_current' INTEGER NOT NULL, 'votes_max' INTEGER NOT NULL)")
                conn.commit()
                print(f"Created voteban table in database for {guild[:len(guild) - 8]}")
                conn.execute(f"INSERT INTO {guild} VALUES(NULL, ?, ?, ?, ?)", (ctx.message.mentions[0].id, ctx.message.author.id, 1, count))
                conn.commit()
                ban_field = discord.Embed(colour = discord.Colour(0xFDED32))
                ban_field.add_field(name = f"Ban vote in progress!", value = f"{ctx.message.mentions[0].mention} `1/{count}`", inline = True)
                await ctx.send(embed = ban_field)

            else:
                data = conn.execute(f"SELECT * FROM {guild} WHERE ban_user = '{ctx.message.mentions[0].id}'").fetchall()

                if len(data) == 0:
                    conn.execute(f"INSERT INTO {guild} VALUES(NULL, ?, ?, ?, ?)", (ctx.message.mentions[0].id, ctx.message.author.id, 1, count))
                    conn.commit()
                    ban_field = discord.Embed(colour = discord.Colour(0xFDED32))
                    ban_field.add_field(name = f"Ban vote in progress!", value = f"{ctx.message.mentions[0].mention} `1/{count}`", inline = True)
                    await ctx.send(embed = ban_field)

                else:
                    data = data[0]
                    ban_user = data[1]
                    ban_voters = data[2].split("_")
                    votes_current = int(data[3])
                    votes_max = int(data[4])

                    if str(ctx.message.author.id) in ban_voters:
                        await ctx.send(f"***{self.doubleVoteResponses[random.randrange(len(self.doubleVoteResponses))]}***")
                    
                    else:
                        if votes_current >= (votes_max - 1):
                            await ctx.guild.get_member(int(ban_user)).kick(reason = f"{self.banKickReasonResponses[random.randrange(len(self.banKickReasonResponses))]}")
                            ban_field = discord.Embed(colour = discord.Colour(0xFDED32))
                            ban_field.add_field(name = f"You did it!", value = f"{ctx.message.mentions[0].mention} is no more.", inline = True)
                            await ctx.send(embed = ban_field)
                            conn.execute(f"DELETE FROM {guild} WHERE kick_user = '{ban_user}'")
                            conn.commit()

                        else:
                            votes_current += 1
                            ban_voters.append(ctx.author.id)
                            ban_voters = "_".join(map(str, ban_voters))
                            conn.execute(f"UPDATE {guild} SET votes_current = '{votes_current}', kick_voters = '{ban_voters}' WHERE kick_user = '{ban_user}'")
                            conn.commit()
                            ban_field = discord.Embed(colour = discord.Colour(0xFDED32))
                            ban_field.add_field(name = f"Ban vote in progress!", value = f"{ctx.message.mentions[0].mention} `{votes_current}/{votes_max}`", inline = True)
                            await ctx.send(embed = ban_field)   
        conn.close()     

    @commands.command(name = "resetVoteBan", aliases = ["rVB", "rvb", "resetvB", "rBan", "rb", "rB"])
    async def resetVoteBan(self, ctx):

        guild = ctx.guild.name.replace("'", "").replace(" ", "_") + "_voteban"
        conn = sqlite.connect("internal.db")

        if len(conn.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{guild}'").fetchall()) == 0:
            await ctx.send("***There is no ban vote going on right now***")

        else:
            if len(ctx.message.mentions) == 0:
                if len(conn.execute(f"SELECT * FROM {guild}").fetchall()) > 0:
                    conn.execute(f"DELETE FROM {guild}")
                    conn.commit()
                    cancel_ban_field = discord.Embed(colour = discord.Colour(0xFDED32))
                    cancel_ban_field.add_field(name = f"Canceled all ban votes!", value = f"They don't have to fear the sword anymore!")
                    await ctx.send(embed = cancel_ban_field)
                else:
                    await ctx.send("***There is no ban vote against anybody on this server***")

            else:
                if len(conn.execute(f"SELECT * FROM {guild} WHERE ban_user = '{ctx.message.mentions[0].id}'").fetchall()) == 0:
                    await ctx.send("***There is no ban vote against this user***")
                else:
                    conn.execute(f"DELETE FROM {guild} WHERE ban_user = '{ctx.message.mentions[0].id}'")
                    cancel_ban_field = discord.Embed(colour = discord.Colour(0xFDED32))
                    cancel_ban_field.add_field(name = f"Canceled ban voting", value = f"{ctx.message.mentions[0].mention} don't have to fear.. For now anyways.")
                    await ctx.send(embed = cancel_ban_field)
        conn.close()


    @voteBan.error
    async def voteBanError(self, ctx, error):
        await ctx.message.channel.send("***I don't have permission to do that!***")
        print(error)

def setup(bot):
    bot.add_cog(voteBan(bot))

def get_prefix(bot, message):
    conn = sqlite.connect("internal.db")
    try:
        return conn.execute(f"SELECT * FROM prefixes WHERE guild_id = {message.guild.id}").fetchall()[0][2]
    except:
        conn.execute(f"INSERT INTO prefixes VALUES(NULL, ?, ?)", (message.guild.id, "."))
        conn.commit()
        return conn.execute(f"SELECT * FROM prefixes WHERE guild_id = {message.guild.id}").fetchall()[0][2]

    conn.close()