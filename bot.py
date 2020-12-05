import os
import discord
from discord.ext import commands
from discord.utils import get
from discord.ext.commands import has_permissions
from dotenv import load_dotenv
import sqlite3 as sqlite
import random as random

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True

def get_prefix(bot, message):
    conn = sqlite.connect("internal.db")
    try:
        return conn.execute(f"SELECT * FROM prefixes WHERE guild_id = {message.guild.id}").fetchall()[0][2]
    except:
        conn.execute(f"INSERT INTO prefixes VALUES(NULL, ?, ?)", (message.guild.id, "."))
        conn.commit()
        return conn.execute(f"SELECT * FROM prefixes WHERE guild_id = {message.guild.id}").fetchall()[0][2]

    conn.close()

bot = commands.Bot(command_prefix = get_prefix, intents = intents)
bot.remove_command("help")

@bot.command()
async def load(ctx, extension):
    cog_managment_field = discord.Embed(colour = discord.Colour(0xFDED32))
    cog_managment_field.set_author(name = "𝓒𝓸𝓰𝓼 𝓶𝓪𝓷𝓪𝓰𝓶𝓮𝓷𝓽")
    try:
        bot.load_extension(f"cogs.{extension}")
        cog_managment_field.add_field(name = f"Module {extension} loaded!", value = f"Hopefully {ctx.author.mention} knows what are they doing.")
        await ctx.send(embed = cog_managment_field)

    except discord.ext.commands.errors.ExtensionAlreadyLoaded:
        cog_managment_field.add_field(name = f"This module {extension} is loaded already!", value = f"If you wanted to reload it, try `{get_prefix(bot, ctx.message)}reload`")
        await ctx.send(embed = cog_managment_field)

    except:
        cog_managment_field.add_field(name = f"I can't find your module named {extension}", value = f"You sure it's supposed to be here?")
        await ctx.send(embed = cog_managment_field)

@bot.command()
async def unload(ctx, extension):
    cog_managment_field = discord.Embed(colour = discord.Colour(0xFDED32))
    cog_managment_field.set_author(name = "𝓒𝓸𝓰𝓼 𝓶𝓪𝓷𝓪𝓰𝓶𝓮𝓷𝓽")
    try:
        bot.unload_extension(f"cogs.{extension}")
        cog_managment_field.add_field(name = f"Module {extension} unloaded!", value = f"I think you didn't need it anyways..")
        await ctx.send(embed = cog_managment_field)

    except discord.ext.commands.errors.ExtensionNotLoaded:
        cog_managment_field.add_field(name = f"Module {extension} isn't loaded!", value = f"You'll have to load it first.")
        await ctx.send(embed = cog_managment_field)

    except:
        cog_managment_field.add_field(name = f"I can't find {extension} anywhere!", value = f"And yes, I'm sure I didn't lose it.")
        await ctx.send(embed = cog_managment_field)

@bot.command()
async def reload(ctx, extension):
    cog_managment_field = discord.Embed(colour = discord.Colour(0xFDED32))
    cog_managment_field.set_author(name = "𝓒𝓸𝓰𝓼 𝓶𝓪𝓷𝓪𝓰𝓶𝓮𝓷𝓽")
    try:
        bot.unload_extension(f"cogs.{extension}")
        bot.load_extension(f"cogs.{extension}")
        cog_managment_field.add_field(name = f"Module {extension} reloaded", value = f"Maybe it'll start working now.")
        await ctx.send(embed = cog_managment_field)

    except discord.ext.commands.errors.ExtensionNotLoaded:
        bot.load_extension(f"cogs.{extension}")
        cog_managment_field.add_field(name = f"Module {extension} wasn't loaded in!", value = f"It is now tho.")
        await ctx.send(embed = cog_managment_field)

    except:
        cog_managment_field.add_field(name = f"Couldn't find {extension}!", value = f"Nothing I can do here.")
        await ctx.send(embed = cog_managment_field)

@bot.command(name = "changePrefix", aliases = ["cP", "cPrefix", "GlobChangePrefix", "cp"])
async def changePrefix(ctx, prefix):
    conn = sqlite.connect("internal.db")
    conn.execute(f"UPDATE prefixes SET prefix = '{prefix}' WHERE guild_id = {ctx.guild.id}")
    conn.commit()
    await ctx.send(f"Prefix changed to ***{prefix}***")
    conn.close()

@bot.command()
async def ping(ctx):
    latency = int(bot.latency * 1000)
    ping_field = discord.Embed(colour = discord.Colour(0xFDED32), title = "Pong")
    ping_field.add_field(name = f"to {ctx.guild}", value = f"{latency}ms", inline = False)
    await ctx.send(embed = ping_field)

# ______________________________________________EVENTS__________________________________________________

@bot.event
async def on_ready():
    conn = sqlite.connect("internal.db")
    for cog_file in os.listdir("./cogs"):
        if cog_file == "voice.py" or cog_file == "ytdl.py":
            pass
        elif cog_file.endswith(".py"):
            bot.load_extension(f"cogs.{cog_file[:-3]}")

    conn.execute(f"CREATE TABLE IF NOT EXISTS prefixes(id integer PRIMARY KEY, 'guild_id' INTEGER NOT NULL, 'prefix' TEXT NOT NULL)")
    print("Created prefix table")
    conn.execute(f"CREATE TABLE IF NOT EXISTS hangmans('id' INTEGER PRIMARY KEY, 'guild_id' TEXT NOT NULL, 'word' TEXT NOT NULL, 'current_tries' INTEGER NOT NULL, 'max_tries' INTEGER NOT NULL, 'guessed_word' TEXT)")
    print("Created table for hangmans")
    conn.execute(f"CREATE TABLE IF NOT EXISTS playlists(id integer PRIMARY KEY, 'user_id' INTEGER NOT NULL, 'name' TEXT NOT NULL, 'songs' TEXT NOT NULL)")
    print("Created prefix table")
    conn.commit()

    if len(conn.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='hangman_word_list'").fetchall()) == 0:
        conn.execute(f"CREATE TABLE IF NOT EXISTS hangman_word_list(id integer PRIMARY KEY, 'word' TEXT NOT NULL, 'max_tries' INTEGER)")
        conn.commit()
        conn.execute(f"INSERT INTO hangman_word_list VALUES(NULL, ?, ?), (NULL, ?, ?), (NULL, ?, ?), (NULL, ?, ?), (NULL, ?, ?), (NULL, ?, ?), (NULL, ?, ?), (NULL, ?, ?), (NULL, ?, ?), (NULL, ?, ?), (NULL, ?, ?), (NULL, ?, ?), (NULL, ?, ?), (NULL, ?, ?), (NULL, ?, ?), (NULL, ?, ?), (NULL, ?, ?)", ["calm", 3, "siege", 4, "flash", 3, "profession", 6, "approval", 5, "production", 5, "ape", 3, "land", 4, "gear", 5, "biology", 6, "glory", 5, "process", 5, "illusion", 6, "disappointment", 8, "monkey", 5, "bird", 4, "cat", 3])
        conn.commit()
        print("Created word bank for hangman")

    print(f"Database ready")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="if someone needs help"))
    print(f"Logged in as {bot.user}")

    conn.close()

@bot.event
async def on_guild_join(guild):
    conn = sqlite.connect("internal.db")
    conn.execute(f"INSERT INTO prefixes VALUES(NULL, ?, ?)", (guild.id, "."))
    conn.commit()
    print("Successfully added prefix for new guild")
    conn.close()

@bot.event
async def on_guild_remove(guild):
    conn = sqlite.connect("internal.db")
    conn.execute(f"DELETE FROM prefixes WHERE guild_id = {guild.id}")
    conn.commit()
    print("Successfully removed guild prefix")
    conn.close()

bot.run(TOKEN)