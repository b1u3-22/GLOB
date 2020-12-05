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
        self.loop = False
        self.songs = []
        self.current_song = {}

    async def get_audio_info(self, song):
        if not song.lower().startswith("http://") or not song.lower().startswith("https://"):
            song = f"ytsearch:{song}"

        with YoutubeDL(self.YTDL_OPTIONS) as ydl:
            info = ydl.extract_info(song, download = False)

        if info['entries'] != []:
            return {"track": info['entries'][0]['url'], "title": info['entries'][0]['title'], "artist": info['entries'][0]['creator'], "duration": info['entries'][0]['duration'], "likes": info['entries'][0]['like_count'], "dislikes": info['entries'][0]['dislike_count']}

        else:
            return {}

    def play_audio(self, ctx):
        if len(self.songs) > 0:

            if self.loop and self.current_song == self.songs[0] and len(self.songs) > 1:
                self.songs.append(self.songs.pop(0))

            self.current_song = self.songs.pop(0)
            self.bot.loop.create_task(self.inform_user(ctx))
            if self.loop:
                self.songs.append(self.current_song)

            ctx.voice_client.play(FFmpegPCMAudio(self.current_song['track'], **self.FFMPEG_OPTIONS), after = lambda error : print(error) if error is not None else self.play_audio(ctx))

    async def inform_user(self, ctx):
        music_field = discord.Embed(colour = discord.Colour(0xFDED32))
        music_field.set_author(name = "𝓜𝓾𝓼𝓲𝓬")
        music_field.title = f"{self.current_song['title']}"
        music_field.add_field(name = f"`{self.current_song['artist']}`", value = f"Artist")
        music_field.add_field(name = f"`{datetime.timedelta(seconds = self.current_song['duration'])}`", value = f"Duration")
        music_field.add_field(name = f"`{self.current_song['likes']}/{self.current_song['dislikes']}`", value = f"Popularity")
        music_field.add_field(name = f"Playing now!", value = f"Requested by {self.current_song['author'].mention}")
        await ctx.send(embed = music_field)

    @commands.command()
    async def join(self, ctx, hello = False):
        music_field = discord.Embed(colour = discord.Colour(0xFDED32))
        music_field.set_author(name = "𝓜𝓾𝓼𝓲𝓬")
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
            music_field.add_field(name = f"Connected to your channel!", value = f"You can use `{get_prefix(self.bot, ctx.message)}play` to start some music")
            await ctx.send(embed = music_field)
            if hello:
                info = await self.get_audio_info("https://www.youtube.com/watch?v=hCiv9wphnME")
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
            music_field.add_field(name = f"I am not connected anywhere!", value = f"You can use `{get_prefix(self.bot, ctx.message)}join` to get me on your channel or `{get_prefix(self.bot, ctx.message)}play` to start some music")
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

            if len(self.songs) == 0 and not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
                self.songs.append(info)
                self.play_audio(ctx)

            else:
                music_field.title = f"{info['title']}"
                music_field.add_field(name = f"`{info['artist']}`", value = f"Artist")
                music_field.add_field(name = f"`{datetime.timedelta(seconds = info['duration'])}`", value = f"Duration")
                music_field.add_field(name = f"`{info['likes']}/{info['dislikes']}`", value = f"Popularity")
                music_field.add_field(name = f"Added to queue", value = f"***Sorry, somebody was faster than you.***")
                if self.loop:
                    self.songs.insert(-1, info)
                else:
                    self.songs.append(info)
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
    async def loop(self, ctx):
        music_field = discord.Embed(colour = discord.Colour(0xFDED32))
        music_field.set_author(name = "𝓜𝓾𝓼𝓲𝓬")
        if self.loop:
            self.loop = False
            music_field.add_field(name = "Song looping off!", value = f"You got tired of it, huh?")

        else:
            self.loop = True
            music_field.add_field(name = "Loop turn on!", value = f"You really like ***this*** song, {ctx.author.mention}?")
            if ctx.voice_client.is_playing() or ctx.voice_client.is_paused and self.songs.empty():
                self.songs.append(self.current_song)

        await ctx.send(embed = music_field)

    @commands.command()
    async def stop(self, ctx):
        music_field = discord.Embed(colour = discord.Colour(0xFDED32))
        music_field.set_author(name = "𝓜𝓾𝓼𝓲𝓬")

        if ctx.voice_client == None:
            music_field.add_field(name = "No songs to be stopped!", value = f"You don't have ny songs in your queue or playing. Use `{get_prefix(self.bot, ctx.message)}play` to play something!")

        else:
            if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                self.songs.clear()

                ctx.voice_client.stop()
                self.current_song = {}
                music_field.add_field(name = "All songs from queue were purged!", value = f"To disconnect me use `{get_prefix(self.bot, ctx.message)}leave` or issue `{get_prefix(self.bot, ctx.message)}play` to play new songs!")

        await ctx.send(embed = music_field)

    @commands.command()
    async def queue(self, ctx):
        music_field = discord.Embed(colour = discord.Colour(0xFDED32))
        music_field.set_author(name = "𝓜𝓾𝓼𝓲𝓬")
        total_duration = 0
        if ctx.voice_client:
            if ctx.voice_client.is_playing or ctx.voice_client.is_paused():
                music_field.title = f"`Now playing` - {self.current_song['title']}"
                if self.songs:
                    for song in self.songs:
                        music_field.add_field(name = f"`{self.songs.index(song) + 1}` - {song['title']} by `{song['artist']}`", value = f"Duration: `{datetime.timedelta(seconds = song['duration'])}` | Popularity: `{song['likes']}/{song['dislikes']}` | Requested by {song['author'].mention}", inline = False)
                        total_duration += song['duration']
                    music_field.add_field(name = f"Total Duration", value = f"`{datetime.timedelta(seconds = total_duration)}`")
                    music_field.add_field(name = f"Number of songs", value = f"`{len(self.songs)}`")
                    music_field.add_field(name = f"Loop", value = f"`{self.loop}`")

                else:
                    music_field.add_field(name = f"Author: `{self.current_song['artist']}`", value = f"Duration: `{datetime.timedelta(seconds = self.current_song['duration'])}` | Popularity: `{self.current_song['likes']}/{self.current_song['dislikes']}` | Requested by {self.current_song['author'].mention}")

            else:
                music_field.add_field(name = f"They are no songs playing!", value = f"If you want to play a new song simply type `{get_prefix(self.bot, ctx.message)}play`")

            await ctx.send(embed = music_field)

    @commands.command()
    async def remove(self, ctx, index):
        index = int(index)
        music_field = discord.Embed(colour = discord.Colour(0xFDED32))
        music_field.set_author(name = "𝓜𝓾𝓼𝓲𝓬")

        if not self.songs and not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
            music_field.add_field(name = "There is no existing queue", value = f"But you can use `{get_prefix(self.bot, ctx.message)}play` to play something!")

        elif index - 1 > len(self.songs):
            music_field.add_field(name = "This song doesn't exist in your queue", value = f"To remove all songs from the queue use `{get_prefix(self.bot, ctx.message)}stop`")

        elif index - 1 <= len(self.songs) and index - 1 >= 0:
            removed_song = self.songs.pop(index - 1)
            music_field.add_field(name = f"{removed_song['title']} has been removed from your queue!", value = f"I bet nobody will miss it anyway")
        await ctx.send(embed = music_field)

    @commands.command()
    async def move(self, ctx, index_of_song, desired_position):
        music_field = discord.Embed(colour = discord.Colour(0xFDED32))
        music_field.set_author(name = "𝓜𝓾𝓼𝓲𝓬")
        index_of_song = int(index_of_song) - 1
        desired_position = int(desired_position) - 1
        if index_of_song >= 0 and desired_position >= 0:
            if index_of_song > len(self.songs):
                music_field.add_field(name = f"There is no song on position `{index_of_song + 1}`", value = f"Did you want to skip? Use `{get_prefix(bot, ctx.message)}skip` Don't worry, if you have loop enabled the song will stay in queue")

            else:
                if desired_position > len(self.songs) - 1:
                    self.songs.append(self.songs.pop(index_of_song))
                    music_field.add_field(name = f"Song `{self.songs[-1]['title']}` was moved to the end of queue from position `{index_of_song + 1}`", value = f"This happened because you entered number greater than the index of last song")
                
                else:
                    self.songs.insert(desired_position, self.songs.pop(index_of_song))
                    music_field.add_field(name = f"I have moved `{self.songs[desired_position]['title']}`from position `{index_of_song + 1}` to `{desired_position + 1}`", value = f"I hope I got it right!")

        await ctx.send(embed = music_field)

    @commands.command()
    async def now(self, ctx):
        music_field = discord.Embed(colour = discord.Colour(0xFDED32))
        music_field.set_author(name = "𝓜𝓾𝓼𝓲𝓬")
        music_field.title = f"`Now playing` - {self.current_song['title']}"
        music_field.add_field(name = f"Author: `{self.current_song['artist']}`", value = f"Duration: `{datetime.timedelta(seconds = self.current_song['duration'])}` | Popularity: `{self.current_song['likes']}/{self.current_song['dislikes']}` | Requested by {self.current_song['author'].mention}")
        await ctx.send(embed = music_field)

    @commands.command()
    async def addToPlaylist(self, ctx, name, *, song_name = None):
        music_field = discord.Embed(colour = discord.Colour(0xFDED32))
        music_field.set_author(name = "𝓜𝓾𝓼𝓲𝓬")
        conn = sqlite.connect("internal.db")
        song_to_save = ""
        if self.current_song == {} and song_name is None:
            music_field.add_field(name = f"You have to specify what song!", value = f"I can't add nothing to playlist..")

        else:
            if song_name == None:
                for value in self.current_song:
                    song_to_save += "|" + str(self.current_song[value])
                song_to_save += "|"
            elif song_name.lower() == "queue":
                for song in self.songs:
                    for value in song:
                        song_to_save += "|" + str(song[value])
                    song_to_save += "|"
                for value in self.current_song:
                    song_to_save += "|" + str(self.current_song[value])
                song_to_save += "|"
            else:
                info = await self.get_audio_info(song_name)
                for value in info:
                    song_to_save += "|" + str(info[value])
                song_to_save += "|"
            if len(conn.execute(f"SELECT * FROM playlists WHERE name = '{name}' AND user_id = '{ctx.author.id}'").fetchall()) == 0:
                conn.execute("INSERT INTO playlists VALUES(NULL, ?, ?, ?)", (ctx.author.id, name, song_to_save))
                conn.commit()
                if song_name == None:
                    music_field.add_field(name = f"`{name}` playlist created! I added `{self.current_song['title']}` into it for you.", value = f"You can add songs to your playlist using `{get_prefix(self.bot, ctx.message)}addToPlaylist {name} song`")
                elif song_name.lower() == "queue":
                    music_field.add_field(name = f"New playlist named `{name}` created! And your queue added into it", value = f"You can play your playlist using `{get_prefix(self.bot, ctx.message)}playPlaylist {name}` or you can add songs to your queue, use `{get_prefix(self.bot, ctx.message)}addToPlaylist {name} queue` to update it")
                else:
                    music_field.add_field(name = f"Created new playlist named `{name}` and added `{self.current_song['title']}` into it", value = f"You can play your playlist using `{get_prefix(self.bot, ctx.message)}playPlaylist {name}` or you can add songs to your queue, use `{get_prefix(self.bot, ctx.message)}addToPlaylist {name} queue` to update it")


            else:
                songs_in_playlist = conn.execute(f"SELECT songs FROM playlists WHERE user_id = '{ctx.author.id}' AND name = '{name}'").fetchall()[0][0]
                conn.execute(f"UPDATE playlists SET songs = '{songs_in_playlist + song_to_save}' WHERE user_id = '{ctx.author.id}' AND name = '{name}'")
                conn.commit()

                if song_name == None:
                    music_field.add_field(name = f"Added your currently playing song named `{self.current_song['title']}` into your playlist `{name}`", value = f"You can play it using `{get_prefix(self.bot, ctx.message)}playPlaylist`")
                else:
                    music_field.add_field(name = f"Added `{info['title']}` into your playlist named `{name}`", value = f"That's nice song you got there, {ctx.author.mention}!")

        conn.close()
        await ctx.send(embed = music_field)

    @commands.command()
    async def updatePlaylist(self, ctx, name):
        music_field = discord.Embed(colour = discord.Colour(0xFDED32))
        music_field.set_author(name = "𝓜𝓾𝓼𝓲𝓬")
        conn = sqlite.connect("internal.db")
        playlists = conn.execute(f"SELECT * FROM playlists WHERE name = '{name}' AND user_id = '{ctx.author.id}'").fetchall()
        if len(playlists) == 0:
            music_field.add_field(name = f"Couldn't find any playlists under the name `{name}`", value = f"But you can create it! Using `{get_prefix(self.bot, ctx.message)}addToPlaylist {name} song`")

        else:
            song_to_save = ""
            for song in self.songs:
                    for value in song:
                        song_to_save += "|" + str(song[value])
                    song_to_save += "|"

            conn.execute(f"UPDATE playlists SET songs = '{song_to_save}' WHERE name = '{name}' AND user_id = '{ctx.author.id}'")
            conn.commit()
            music_field.add_field(name = f"Updated playlist `{name}` according to your queue", value = f"You can now display the updated version using `{get_prefix(self.bot, ctx.message)}displayPlaylist {name}`")

        conn.close()
        await ctx.send(embed = music_field)

    @commands.command()
    async def playPlaylist(self, ctx, name):
        music_field = discord.Embed(colour = discord.Colour(0xFDED32))
        music_field.set_author(name = "𝓜𝓾𝓼𝓲𝓬")
        conn = sqlite.connect("internal.db")
        if len(ctx.message.mentions) == 0:
            data = conn.execute(f"SELECT * FROM playlists WHERE name = '{name}'").fetchall()

        else:
            data = conn.execute(f"SELECT * FROM playlists WHERE name = '{name}' user_id = '{ctx.message.mentions[0].id}'").fetchall()

        if len(data) != 0:
            songs = data[0][3].split("||")
            user_id = data[0][1]
            song_titles = []
            for song in songs:
                song = song.split("|")
                for i in range(len(song) - 1):
                    if song[i] == "":
                        song.pop(i)
                song_titles.append(song[1])
                print(song_titles)

            self.songs.clear
            if not ctx.voice_client:
                await ctx.author.voice.channel.connect()

            if not ctx.voice_client.is_playing() or not ctx.voice_client.is_paused():
                song = await self.get_audio_info(song_titles[0])
                song['author'] = ctx.guild.get_member(user_id)
                self.songs.append(song)
                self.play_audio(ctx)
                for i in range(1, len(song_titles)):
                    song = await self.get_audio_info(song_titles[i])
                    song['author'] = ctx.guild.get_member(user_id)
                    self.songs.append(song)

            else:
                for i in range(len(song_titles) - 1):
                    song = await self.get_audio_info(song_titles[i])
                    song['author'] = ctx.guild.get_member(user_id)
                    self.songs.append(song)

            music_field.add_field(name = f"Replaced your queue with songs from playlist `{name}`", value = f"If you add any songs to your queue, you can update your playlist using `{get_prefix(self.bot, ctx.message)}addToPlaylist {name} update`")

        else:
            music_field.add_field(name = f"I couldn't find any playlist under name `{name}`", value = f"Don't worry, you can always create a new one with this name using `{get_prefix(self.bot, ctx.message)}addToPlaylist {name} song`")

        conn.close()
        await ctx.send(embed = music_field)

# return {"track": info['entries'][0]['url'], "title": info['entries'][0]['title'], "artist": info['entries'][0]['creator'], "duration": info['entries'][0]['duration'], "likes": info['entries'][0]['like_count'], "dislikes": info['entries'][0]['dislike_count']}

    @commands.command()
    async def displayPlaylist(self, ctx, name):
        music_field = discord.Embed(colour = discord.Colour(0xFDED32))
        music_field.set_author(name = "𝓜𝓾𝓼𝓲𝓬")
        conn = sqlite.connect("internal.db")
        if len(ctx.message.mentions) == 0:
            data = conn.execute(f"SELECT * FROM playlists WHERE name = '{name}'").fetchall()

        else:
            data = conn.execute(f"SELECT * FROM playlists WHERE name = '{name}' user_id = '{ctx.message.mentions[0].id}'").fetchall()

        if len(data) != 0:
            total_duration = 0
            songs = data[0][3].split("||")
            user = ctx.guild.get_member(data[0][1])
            playlist_name = data[0][2]
            songs_to_display = []
            for song in songs:
                song = song.split("|")
                for i in range(len(song) - 1):
                    if song[i] == "":
                        song.pop(i)
                song = {'track': song[0], 'title': song[1], 'artist': song[2], 'duration': float(song[3]), 'likes': int(song[4]), 'dislikes': int(song[5]), 'author': user}
                songs_to_display.append(song)

            music_field.title = f"`Playlist` {playlist_name}"      
            for song in songs_to_display:
                music_field.add_field(name = f"`{songs_to_display.index(song) + 1}` - {song['title']} by `{song['artist']}`", value = f"Duration: `{datetime.timedelta(seconds = song['duration'])}` | Popularity: `{song['likes']}/{song['dislikes']}` | Requested by {song['author'].mention}", inline = False)
                total_duration += song['duration']
            music_field.add_field(name = f"Total Duration", value = f"`{datetime.timedelta(seconds = total_duration)}`")
            music_field.add_field(name = f"Number of songs", value = f"`{len(songs_to_display)}`")
            music_field.add_field(name = f"Creator of {name}", value = f"{user.mention}")

        else:
            music_field.add_field(name = f"Couldn't find any playlists under the name `{name}`", value = f"But you can create it! Using `{get_prefix(self.bot, ctx.message)}addToPlaylist {name} song`")

        conn.close()
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