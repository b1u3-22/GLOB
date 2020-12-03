import discord
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions
import sqlite3 as sqlite
import random as random
from youtube_dl import YoutubeDL
from discord import FFmpegPCMAudio
import asyncio
import datetime
import queue
class music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.YTDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': True, 'default-search': 'auto', 'quiet': True, 'extractaudio': True, 'audioformat': 'mp3'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        self.songs = queue.Queue()

    async def get_audio_info(self, song):
        if not song.lower().startswith("http://") or not song.lower().startswith("https://"):
            song = f"ytsearch:{song}"

        with YoutubeDL(self.YTDL_OPTIONS) as ydl:
            info = ydl.extract_info(song, download = False)

        if info['entries'] != []:
            return {"track": info['entries'][0]['url'], "title": info['entries'][0]['title'], "artist": info['entries'][0]['creator'], "duration": datetime.timedelta(seconds = info['entries'][0]['duration']), "likes": info['entries'][0]['like_count'], "dislikes": info['entries'][0]['dislike_count']}

        else:
            return {}

    def play_audio(self, ctx):
        if not self.songs.empty():
            ctx.voice_client.play(FFmpegPCMAudio(self.songs.get(), **self.FFMPEG_OPTIONS), after = lambda error : print(error) if error is not None else self.play_audio(ctx))

    @commands.command()
    async def join(self, ctx):
        music_field = discord.Embed(colour = discord.Colour(0xFDED32))
        music_field.set_author(name = "𝓜𝓾𝓼𝓲𝓬")
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
            music_field.add_field(name = f"Connected to your channel!", value = f"You can use `{get_prefix(self.bot, ctx.message)}play` to start some music")
            await ctx.send(embed = music_field)
            info = self.get_audio_info("https://www.youtube.com/watch?v=hCiv9wphnME")
            ctx.voice_client.play(FFmpegPCMAudio(info['track'], **self.FFMPEG_OPTIONS))

        else:
            await ctx.send("You have to be connected in voice channel")

    @commands.command()
    async def leave(self, ctx):
        music_field = discord.Embed(colour = discord.Colour(0xFDED32))
        music_field.set_author(name = "𝓜𝓾𝓼𝓲𝓬")
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            music_field.add_field(name = f"Disconnected from voice channel!", value = f"And until next time, have a great time!")
            await ctx.send(embed = music_field)

        else:
            music_field.add_field(name = f"I am not connected anywhere!", value = f"You can use `{get_prefix(self.bot, ctx.message)}join` to get me on your channel or `{get_prefix(bot, ctx.message)}play` to start some music")
            await ctx.send(embed = music_field)

    @commands.command()
    async def play(self, ctx, *, song):
        music_field = discord.Embed(colour = discord.Colour(0xFDED32))
        music_field.set_author(name = "𝓜𝓾𝓼𝓲𝓬")
        if ctx.author.voice:
            if ctx.voice_client == None:
                await ctx.author.voice.channel.connect()

            info = await self.get_audio_info(song)

            music_field.title = f"{info['title']}"
            music_field.add_field(name = f"`{info['artist']}`", value = f"Artist")
            music_field.add_field(name = f"`{info['duration']}`", value = f"Duration")
            music_field.add_field(name = f"`{info['likes']}/{info['dislikes']}`", value = f"Popularity")

            if self.songs.empty() and not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
                music_field.add_field(name = f"Playing now!", value = f"***\n***")
                self.songs.put(info['track'])
                self.play_audio(ctx)
                await ctx.send(embed = music_field)

            else:
                music_field.add_field(name = f"Added to queue", value = f"***\n***")
                self.songs.put(info['track'])
                await ctx.send(embed = music_field)

                
    @commands.command()
    async def pause(self, ctx):
        if ctx.voice_client == None:
            await ctx.send("Nothing to be paused")
        else:
            if ctx.voice_client.is_playing():
                ctx.voice_client.pause()
                await ctx.send("Paused")

            else:
                await ctx.send("I'm not playing anything")

    @commands.command()
    async def resume(self, ctx):
        if ctx.voice_client == None:
            await ctx.send("Nothing paused")
        else:
            if not ctx.voice_client.is_playing():
                ctx.voice_client.resume()
                await ctx.send("Resumed")

            else:
                await ctx.send("Already playing")

    @commands.command()
    async def skip(self, ctx):
        if ctx.voice_client == None:
            await ctx.send("Nothing to be skipped")
        else:
            if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                ctx.voice_client.stop()
                await ctx.send("Skipped")

    @commands.command()
    async def stop(self, ctx):
        if ctx.voice_client == None:
            await ctx.send("I'm not even connected anywhere!")

        else:
            if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                with self.songs.mutex:
                    self.songs.queue.clear()

                ctx.voice_client.stop()
                await ctx.send("Cleared your queue!")

def setup(bot):
    bot.add_cog(music(bot))

def get_prefix(bot, message):
    conn = sqlite.connect("internal.db")
    try:
        return conn.execute(f"SELECT * FROM prefixes WHERE guild_id = {message.guild.id}").fetchall()[0][2]
    except:
        conn.execute(f"INSERT INTO prefixes VALUES(NULL, ?, ?)", (message.guild.id, "."))
        conn.commit()
        return conn.execute(f"SELECT * FROM prefixes WHERE guild_id = {message.guild.id}").fetchall()[0][2]

    conn.close()