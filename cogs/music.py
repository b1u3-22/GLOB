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
        self.current_song = {}

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
            self.current_song = self.songs.get()
            self.bot.loop.create_task(self.inform_user(ctx))
            ctx.voice_client.play(FFmpegPCMAudio(self.current_song['track'], **self.FFMPEG_OPTIONS), after = lambda error : print(error) if error is not None else self.play_audio(ctx))

    async def inform_user(self, ctx):
        music_field = discord.Embed(colour = discord.Colour(0xFDED32))
        music_field.set_author(name = "𝓜𝓾𝓼𝓲𝓬")
        music_field.title = f"{self.current_song['title']}"
        music_field.add_field(name = f"`{self.current_song['artist']}`", value = f"Artist")
        music_field.add_field(name = f"`{self.current_song['duration']}`", value = f"Duration")
        music_field.add_field(name = f"`{self.current_song['likes']}/{self.current_song['dislikes']}`", value = f"Popularity")
        music_field.add_field(name = f"Playing now!", value = f"Requested by {self.current_song['author'].mention}")
        await ctx.send(embed = music_field)

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
            info['author'] = ctx.author

            if self.songs.empty() and not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
                self.songs.put(info)
                self.play_audio(ctx)

            else:
                music_field.title = f"{info['title']}"
                music_field.add_field(name = f"`{info['artist']}`", value = f"Artist")
                music_field.add_field(name = f"`{info['duration']}`", value = f"Duration")
                music_field.add_field(name = f"`{info['likes']}/{info['dislikes']}`", value = f"Popularity")
                music_field.add_field(name = f"Added to queue", value = f"***Sorry, somebody was faster than you.***")
                self.songs.put(info)
                await ctx.send(embed = music_field)

                
    @commands.command()
    async def pause(self, ctx):
        music_field = discord.Embed(colour = discord.Colour(0xFDED32))
        music_field.set_author(name = "𝓜𝓾𝓼𝓲𝓬")

        if ctx.voice_client == None:
            music_field.add_field(name = "Nothing to be paused!", value = f"This commands purpose is to pause currently playing song. To play song use `{get_prefix(self.bot, ctx.message)}play`")
        else:
            if ctx.voice_client.is_playing():
                music_field.add_field(name = f"{self.current_song['title']} paused!", value = f"Song is now paused if you want to resume it, you can use `{get_prefix(self.bot, ctx.message)}resume`")
                ctx.voice_client.pause()

            else:
                music_field.add_field(name = f"{self.current_song['title']} is already paused!", value = f"To resume it use `{get_prefix(self.bot, ctx.message)}resume`")

        await ctx.send(embed = music_field)

    @commands.command()
    async def resume(self, ctx):
        music_field = discord.Embed(colour = discord.Colour(0xFDED32))
        music_field.set_author(name = "𝓜𝓾𝓼𝓲𝓬")

        if ctx.voice_client == None:
            music_field.add_field(name = "Nothing to be resumed!", value = f"If you want to start some music use `{get_prefix(self.bot, ctx.message)}play`")
        else:
            if ctx.voice_client.is_paused():
                music_field.add_field(name = f"{self.current_song['title']} resumed!", value = f"Let the show start again!")
                ctx.voice_client.resume()

            else:
                music_field.add_field(name = f"{self.current_song['title']} is playing already!", value = f"You can pause it using `{get_prefix(self.bot, ctx.message)}pause`")

        await ctx.send(embed = music_field)

    @commands.command()
    async def skip(self, ctx):
        music_field = discord.Embed(colour = discord.Colour(0xFDED32))
        music_field.set_author(name = "𝓜𝓾𝓼𝓲𝓬")

        if ctx.voice_client == None:
            music_field.add_field(name = "Nothing to be skipped!", value = f"It seems you have no songs playing nor in queue. Don't worry, use `{get_prefix(self.bot, ctx.message)}play` to play something!")

        else:
            if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                music_field.add_field(name = f"{self.current_song['title']} skipped!", value = f"You didn't like it, I see")
                ctx.voice_client.stop()

        await ctx.send(embed = music_field)


    @commands.command()
    async def stop(self, ctx):
        music_field = discord.Embed(colour = discord.Colour(0xFDED32))
        music_field.set_author(name = "𝓜𝓾𝓼𝓲𝓬")

        if ctx.voice_client == None:
            music_field.add_field(name = "No songs to be stopped!", value = f"You don't have ny songs in your queue or playing. Use `{get_prefix(self.bot, ctx.message)}play` to play something!")

        else:
            if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                with self.songs.mutex:
                    self.songs.queue.clear()

                ctx.voice_client.stop()
                music_field.add_field(name = "All songs from queue were purged!", value = f"To disconnect me use `{get_prefix(self.bot, ctx.message)}leave` or issue `{get_prefix(self.bot, ctx.message)}play` to play new songs!")

        await ctx.send(embed = music_field)

    @commands.command()
    async def queue(self, ctx):
        music_field = discord.Embed(colour = discord.Colour(0xFDED32))
        music_field.set_author(name = "𝓜𝓾𝓼𝓲𝓬")

        if ctx.voice_client:
            if ctx.voice_client.is_playing or ctx.voice_client.is_paused():
                music_field.title = f"`Now playing` - {self.current_song['title']}"
                if not self.songs.empty():
                    for song in self.songs.queue:
                        music_field.add_field(name = f"`{self.songs.queue.index(song) + 1}` - {song['title']} by `{song['artist']}`", value = f"Duration: `{song['duration']}` | Popularity: `{song['likes']}/{song['dislikes']}` | Requested by {song['author'].mention}", inline = False)

                else:
                    music_field.add_field(name = f"Author: `{self.current_song['artist']}`", value = f"Duration: `{self.current_song['duration']}` | Popularity: `{self.current_song['likes']}/{self.current_song['dislikes']}` | Requested by {self.current_song['author'].mention}")

            else:
                music_field.add_field(name = f"They are no songs playing!", value = f"If you want to play a new song simply type `{get_prefix(self.bot, ctx.message)}play`")

            await ctx.send(embed = music_field)

                    

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