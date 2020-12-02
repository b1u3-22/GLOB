import discord
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions
import sqlite3 as sqlite
import random as random
from youtube_dl import YoutubeDL
from discord import FFmpegPCMAudio
import asyncio
import datetime

class music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.YTDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': True, 'default-search': 'auto', 'quiet': True, 'extractaudio': True, 'audioformat': 'mp3'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    def get_audio_info(self, song):
        if not song.lower().startswith("http://") or not song.lower().startswith("https://"):
            song = f"ytsearch:{song}"

        with YoutubeDL(self.YTDL_OPTIONS) as ydl:
            info = ydl.extract_info(song, download = False)

        if info['entries'] != []:
            title = info['entries'][0]['title']
            creator = info['entries'][0]['creator']
            duration = info['entries'][0]['duration']
            likes = info['entries'][0]['like_count']
            dislikes = info['entries'][0]['dislike_count']
            track = info['entries'][0]['url']
            return [track, title, creator, duration, likes, dislikes]

        else:
            return False      
    
    @commands.command()
    async def join(self, ctx):
        music_field = discord.Embed(colour = discord.Colour(0xFDED32))
        music_field.set_author(name = "𝓜𝓾𝓼𝓲𝓬")
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
            music_field.add_field(name = f"Connected to your channel!", value = f"You can use `{get_prefix(self.bot, ctx.message)}play` to start some music")
            await ctx.send(embed = music_field)
            info = self.get_audio_info("https://www.youtube.com/watch?v=hCiv9wphnME")
            ctx.voice_client.play(FFmpegPCMAudio(info[0], **self.FFMPEG_OPTIONS))

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

            info = self.get_audio_info(song)
            if not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
                if info:
                    player = ctx.voice_client.play(FFmpegPCMAudio(info[0], **self.FFMPEG_OPTIONS))
                    await self.songs.put(player)
                    music_field.title = f"{info[1]}"
                    music_field.add_field(name = f"Created by {info[2]}", value = f"Duration: {str(datetime.timedelta(seconds = info[3]))}\n Likes: {info[4]}\n Dislikes: {info[5]}\n")
                    await ctx.send(embed = music_field)

                else:
                    music_field.title = f"{song}"
                    music_field.add_field(name = f"I couldn't find any songs", value = f"Try to be less specific or enter an url")

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
    async def stop(self, ctx):
        if ctx.voice_client == None:
            await ctx.send("Nothing to be stopped")
        else:
            if ctx.voice_client.is_playing():
                ctx.voice_client.stop()
                await ctx.send("Stopped")

            else:
                await ctx.send("I'm not playing anything")

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