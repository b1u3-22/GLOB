import random
import discord
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions
import apraw
from dotenv import load_dotenv
import os

load_dotenv()
REDDIT_USERNAME = os.getenv('REDDIT_USERNAME')
REDDIT_PASSWORD = os.getenv('REDDIT_PASSWORD')
REDDIT_SECRET = os.getenv('REDDIT_SECRET')
REDDIT_USERAGENT = os.getenv('REDDIT_USERAGENT')
REDDIT_ID = os.getenv('REDDIT_ID')

class reddit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reddit = apraw.Reddit(
                username=REDDIT_USERNAME,
                client_secret=REDDIT_SECRET,
                password=REDDIT_PASSWORD,
                user_agent=REDDIT_USERAGENT,
                client_id=REDDIT_ID
            )

    @commands.command()
    async def cat(self, ctx):
        subreddit = await self.reddit.subreddit("cats")
        post = await subreddit.random()
        while not (post.url.startswith("https://i.redd.it") and post.url.endswith(".jpg")):
            post = await subreddit.random()

        await ctx.send(post.url)

    @commands.command()
    async def birb(self, ctx):
        subreddit = await self.reddit.subreddit("Birbs")
        post = await subreddit.random()
        while not (post.url.startswith("https://i.redd.it") and post.url.endswith(".jpg")):
            post = await subreddit.random()

        await ctx.send(post.url)
    
    @commands.command()
    async def meme(self, ctx):
        subreddit = await self.reddit.subreddit("memes")
        post = await subreddit.random()
        while not (post.url.startswith("https://i.redd.it") and post.url.endswith(".jpg")):
            post = await subreddit.random()

        await ctx.send(post.url)

    @commands.command(name="programmerhumor", aliases=["programmermeme", "progmeme"])
    async def programmerhumor(self, ctx):
        subreddit = await self.reddit.subreddit("ProgrammerHumor")
        post = await subreddit.random()
        while not (post.url.startswith("https://i.redd.it") and post.url.endswith(".jpg")):
            post = await subreddit.random()

        await ctx.send(post.url)

    @commands.command()
    async def space(self, ctx):
        subreddit = await self.reddit.subreddit("Spaceporn")
        post = await subreddit.random()
        while not (post.url.startswith("https://i.redd.it") and post.url.endswith(".jpg")):
            post = await subreddit.random()

        await ctx.send(post.url)

    @commands.command()
    async def earth(self, ctx):
        subreddit = await self.reddit.subreddit("EarthPorn")
        post = await subreddit.random()
        while not (post.url.startswith("https://i.redd.it") and post.url.endswith(".jpg")):
            post = await subreddit.random()

        await ctx.send(post.url)


    @commands.command()
    async def subreddit(self, ctx, subredditname):
        subreddit = await self.reddit.subreddit(subredditname)
        try:
            post = await subreddit.random()
        except KeyError:
            await ctx.send("Sorry, the subreddit you gave me doesn't exist")
            return ""
        
        while not (post.url.startswith("https://i.redd.it") and post.url.endswith(".jpg")):
            post = await subreddit.random()

        await ctx.send(post.url)

def setup(bot):
    bot.add_cog(reddit(bot))

def get_prefix(bot, message):
    conn = sqlite.connect("data/internal.db")
    try:
        return conn.execute(f"SELECT * FROM prefixes WHERE guild_id = {message.guild.id}").fetchall()[0][2]
    except:
        conn.execute(f"INSERT INTO prefixes VALUES(NULL, ?, ?)", (message.guild.id, "."))
        conn.commit()
        return conn.execute(f"SELECT * FROM prefixes WHERE guild_id = {message.guild.id}").fetchall()[0][2]

    conn.close()