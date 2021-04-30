import discord
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions
import sqlite3 as sqlite
import random as random
from youtube_dl import YoutubeDL
from discord import FFmpegPCMAudio
import asyncio
import datetime
#from discord_slash import cog_ext, SlashContext

class music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.YTDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': True, 'default-search': 'auto', 'quiet': True, 'extractaudio': True, 'audioformat': 'mp3', 'rm-cache-dir': True}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        self.loop = False
        self.songs = []
        self.current_song = {}

        conn = sqlite.connect("data/internal.db")
        conn.execute("CREATE TABLE IF NOT EXISTS music(id INTEGER PRIMARY KEY, guild_id INTEGER NOT NULL, current_song TEXT, queued_songs TEXT, loop INTEGER NOT NULL)")

    def songs_to_string(self, songs):
        output = ""
        for song in songs:
            output += f"|{song['track']}|{song['title']}|{song['artist']}|{song['duration']}|{song['likes']}|{song['dislikes']}|{song['link']}|{song['author']}|"

        return output

    def song_to_string(self, song):
        return f"|{song['track']}|{song['title']}|{song['artist']}|{song['duration']}|{song['likes']}|{song['dislikes']}|{song['link']}|{song['author']}|"

    def songs_from_string(self, songs):
        if songs == "" or songs == None or not songs:
            return []
        songs = songs.split("||")
        output = []
        for song in songs:
            if song == "":
                pass
            else:
                song = list(filter(None, song.split("|")))

                output.append({'track': song[0], 'title': song[1], 'artist': song[2], 'duration': song[3], 'likes': song[4], 'dislikes': song[5], 'link': song[6], 'author': song[7]})

        return output

    def song_from_string(self, song):
        song = song.split("|")
        return {'track': song[1], 'title': song[2], 'artist': song[3], 'duration': song[4], 'likes': song[5], 'dislikes': song[6], 'link': song[7], 'author': song[8]}

    def write_to_db(self, ctx, song):
        conn = sqlite.connect("data/internal.db")
        song_to_store = f"|{song['track']}|{song['title']}|{song['artist']}|{song['duration']}|{song['likes']}|{song['dislikes']}|{song['link']}|{song['author']}|"
        if len(conn.execute(f"SELECT * FROM music WHERE guild_id = {ctx.guild.id}").fetchall()) == 0:
            conn.execute("INSERT INTO music VALUES(NULL, ?, ?, ?, ?)", [ctx.guild.id, "", song_to_store, 0])
        else:
            guild_music = conn.execute(f"SELECT * FROM music WHERE guild_id = {ctx.guild.id}").fetchall()[0]
            guild_loop = guild_music[4]
            guild_music = self.songs_from_string(guild_music[3])
            if guild_loop == 1:
                guild_music.insert(-1, song)
            else:
                guild_music.append(song)
            conn.execute(f"UPDATE music SET queued_songs = ? WHERE guild_id = ?", (self.songs_to_string(guild_music), ctx.guild.id))

        conn.commit()
        conn.close()

    def get_audio_info(self, song):
        if not song.lower().startswith("http://") or not song.lower().startswith("https://"):
            song = f"ytsearch:{song}"

        with YoutubeDL(self.YTDL_OPTIONS) as ydl:
            info = ydl.extract_info(song, download = False)

        if info['entries'] != []:

            print(info['entries'][0])

            try:
                creator = info['entries'][0]['creator']

            except KeyError:
                creator = info['entries'][0]['uploader_id']

            return {"track": info['entries'][0]['url'],
                    "title": info['entries'][0]['title'],
                    "artist": creator, 
                    "duration": info['entries'][0]['duration'], 
                    "likes": info['entries'][0]['like_count'], 
                    "dislikes": info['entries'][0]['dislike_count'],
                    "link": "https://www.youtube.com/watch?v=" +  info['entries'][0]['id']
                    }

        else:
            return {}

    def play_audio(self, ctx):

        conn = sqlite.connect("data/internal.db")
        guild_info = conn.execute(f"SELECT * FROM music WHERE guild_id = {ctx.guild.id}").fetchall()[0]
        songs = self.songs_from_string(guild_info[3])
        current_song = "" if conn.execute(f"SELECT * FROM music WHERE guild_id = {ctx.guild.id}").fetchall()[0][2] == "" else self.song_from_string(guild_info[2])
        loop = guild_info[4]

        if len(songs) > 0:

            if loop == 1 and current_song == songs[0] and len(songs) > 1:
                songs.append(songs.pop(0))

            current_song = songs.pop(0)

            self.bot.loop.create_task(self.inform_user(ctx))

            if loop == 1:
                songs.append(current_song)

            conn.execute(f"UPDATE music SET current_song = ?, queued_songs = ? WHERE guild_id = ?", (self.song_to_string(current_song), self.songs_to_string(songs), ctx.guild.id))
            conn.commit()
            conn.close()
            ctx.voice_client.play(FFmpegPCMAudio(current_song['track'], **self.FFMPEG_OPTIONS), after = lambda error: print(error) if error is not None else self.play_audio(ctx))

    async def inform_user(self, ctx):
        conn = sqlite.connect("data/internal.db")
        current_song = self.songs_from_string(conn.execute(f"SELECT * FROM music WHERE guild_id = {ctx.guild.id}").fetchall()[0][2])[0]
        conn.close()
        music_field = discord.Embed(colour = discord.Colour(0xFDED32))
        music_field.set_author(name = "𝓜𝓾𝓼𝓲𝓬")
        music_field.title = f"{current_song['title']}"
        music_field.add_field(name = f"`{current_song['artist']}`", value = f"Artist")
        music_field.add_field(name = f"`{datetime.timedelta(seconds = int(current_song['duration']))}`", value = f"Duration")
        music_field.add_field(name = f"`{current_song['likes']}/{current_song['dislikes']}`", value = f"Popularity")
        author = await ctx.guild.fetch_member(current_song['author'])
        music_field.add_field(name = f"Playing now!", value = f"Requested by { author.mention}")
        await ctx.send(embed = music_field)

    #@cog_ext.cog_slash(name="join")
    @commands.command()
    async def join(self, ctx, hello = ""):
        music_field = discord.Embed(colour = discord.Colour(0xFDED32))
        music_field.set_author(name = "𝓜𝓾𝓼𝓲𝓬")
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
            music_field.add_field(name = f"Connected to your channel!", value = f"You can use `{get_prefix(self.bot, ctx.message)}play` to start some music")
            await ctx.send(embed = music_field)
            if hello != "":
                info = self.get_audio_info("https://www.youtube.com/watch?v=hCiv9wphnME")
                ctx.voice_client.play(FFmpegPCMAudio(info['track'], **self.FFMPEG_OPTIONS))

        else:
            await ctx.send("You have to be connected in voice channel")

    #@cog_ext.cog_slash(name="leave")
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

    #@cog_ext.cog_slash(name="play")
    @commands.command()
    async def play(self, ctx, *, song):

        music_field = discord.Embed(colour = discord.Colour(0xFDED32))
        music_field.set_author(name = "𝓜𝓾𝓼𝓲𝓬")

        if ctx.author.voice:
            if ctx.voice_client == None:
                await ctx.author.voice.channel.connect()

            info = self.get_audio_info(song)
            info['author'] =  ctx.author.id

            if not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
                self.write_to_db(ctx, info)
                self.play_audio(ctx)

            else:
                music_field.title = f"{info['title']}"
                music_field.add_field(name = f"`{info['artist']}`", value = f"Artist")
                music_field.add_field(name = f"`{datetime.timedelta(seconds = info['duration'])}`", value = f"Duration")
                music_field.add_field(name = f"`{info['likes']}/{info['dislikes']}`", value = f"Popularity")
                music_field.add_field(name = f"Added to queue", value = f"***Sorry, somebody was faster than you.***")
                
                self.write_to_db(ctx, info)

                await ctx.send(embed = music_field)

    #@cog_ext.cog_slash(name="pause")
    @commands.command()
    async def pause(self, ctx):
        music_field = discord.Embed(colour = discord.Colour(0xFDED32))
        music_field.set_author(name = "𝓜𝓾𝓼𝓲𝓬")
        conn = sqlite.connect("data/internal.db")

        if ctx.voice_client == None:
            music_field.add_field(name = "Nothing to be paused!", value = f"This commands purpose is to pause currently playing song. To play song use `{get_prefix(self.bot, ctx.message)}play`")
        else:
            current_song = self.song_from_string(conn.execute("SELECT current_song FROM music WHERE guild_id = ?", (ctx.guild.id, )).fetchall()[0][0])
            conn.close()
            if ctx.voice_client.is_playing():
                music_field.add_field(name = f"{current_song['title']} paused!", value = f"Song is now paused if you want to resume it, you can use `{get_prefix(self.bot, ctx.message)}resume`")
                ctx.voice_client.pause()

            else:
                music_field.add_field(name = f"{current_song['title']} is already paused!", value = f"To resume it use `{get_prefix(self.bot, ctx.message)}resume`")
        await ctx.send(embed = music_field)

    #@cog_ext.cog_slash(name="resume")
    @commands.command()
    async def resume(self, ctx):
        music_field = discord.Embed(colour = discord.Colour(0xFDED32))
        music_field.set_author(name = "𝓜𝓾𝓼𝓲𝓬")
        conn = sqlite.connect("data/internal.db")

        if ctx.voice_client == None:
            music_field.add_field(name = "Nothing to be resumed!", value = f"If you want to start some music use `{get_prefix(self.bot, ctx.message)}play`")
        else:
            current_song = self.song_from_string(conn.execute("SELECT current_song FROM music WHERE guild_id = ?", (ctx.guild.id, )).fetchall()[0][0])
            conn.close()
            if ctx.voice_client.is_paused():
                music_field.add_field(name = f"{current_song['title']} resumed!", value = f"Let the show start again!")
                ctx.voice_client.resume()

            else:
                music_field.add_field(name = f"{current_song['title']} is playing already!", value = f"You can pause it using `{get_prefix(self.bot, ctx.message)}pause`")

        await ctx.send(embed = music_field)

    #@cog_ext.cog_slash(name="skip")
    @commands.command()
    async def skip(self, ctx):
        music_field = discord.Embed(colour = discord.Colour(0xFDED32))
        music_field.set_author(name = "𝓜𝓾𝓼𝓲𝓬")
        conn = sqlite.connect("data/internal.db")

        if ctx.voice_client == None:
            music_field.add_field(name = "Nothing to be skipped!", value = f"It seems you have no songs playing nor in queue. Don't worry, use `{get_prefix(self.bot, ctx.message)}play` to play something!")

        else:
            if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                current_song = self.song_from_string(conn.execute("SELECT current_song FROM music WHERE guild_id = ?", (ctx.guild.id, )).fetchall()[0][0])
                conn.close()
                music_field.add_field(name = f"{current_song['title']} skipped!", value = f"You didn't like it, I see")
                ctx.voice_client.stop()

        await ctx.send(embed = music_field)

    #@cog_ext.cog_slash(name="loop")
    @commands.command()
    async def loop(self, ctx):
        music_field = discord.Embed(colour = discord.Colour(0xFDED32))
        music_field.set_author(name = "𝓜𝓾𝓼𝓲𝓬")
        conn = sqlite.connect("data/internal.db")
        if len(conn.execute("SELECT * FROM music WHERE guild_id = ?", (ctx.guild.id, )).fetchall()) == 0:
            conn.execute("INSERT INTO music VALUES(NULL, ?, ?, ?, ?)", ("", "", 1, ctx.guild.id))
            music_field.add_field(name = "Loop turn on!", value = f"To enjoy the sweet music before you start hatin' it, {ctx.author.mention}?")
            conn.commit()
            conn.close()

        else:

            loop = True if conn.execute("SELECT loop FROM music WHERE guild_id = ?", (ctx.guild.id, )).fetchall()[0] == 1 else False

            if loop:
                conn.execute("UPDATE music SET loop = ? WHERE guild_id = ?", (0, ctx.guild.id))
                conn.commit()
                conn.close()
                music_field.add_field(name = "Song looping off!", value = f"You got tired of it, huh?")

            else:
                conn.execute("UPDATE music SET loop = ? WHERE guild_id = ?", (1, ctx.guild.id))
                conn.commit()
                music_field.add_field(name = "Loop turn on!", value = f"You really like ***this*** song, {ctx.author.mention}?")
                songs = self.songs_from_string(conn.execute(f"SELECT queued_songs FROM music WHERE guild_id = {ctx.guild.id}").fetchall()[0][0])

                if ctx.voice_client.is_playing() or ctx.voice_client.is_paused and self.songs.empty():
                    conn.execute("UPDATE music SET queued_songs = ? WHERE guild_id = ?", (conn.execute("SELECT current_song FROM music WHERE guild_id = ?", (ctx.guild.id, )).fetchall()[0][0], ctx.guild.id))
                    conn.commit()

                conn.close()

        await ctx.send(embed = music_field)

    #@cog_ext.cog_slash(name="stop")
    @commands.command()
    async def stop(self, ctx):
        music_field = discord.Embed(colour = discord.Colour(0xFDED32))
        music_field.set_author(name = "𝓜𝓾𝓼𝓲𝓬")
        conn = sqlite.connect("data/internal.db")

        if ctx.voice_client == None:
            music_field.add_field(name = "No songs to be stopped!", value = f"You don't have ny songs in your queue or playing. Use `{get_prefix(self.bot, ctx.message)}play` to play something!")

        else:
            if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                conn.execute("UPDATE music SET queued_songs = ?, current_song = ? WHERE guild_id = ?", ("", "", ctx.guild.id))
                conn.commit()
                ctx.voice_client.stop()
                music_field.add_field(name = "All songs from queue were purged!", value = f"To disconnect me use `{get_prefix(self.bot, ctx.message)}leave` or issue `{get_prefix(self.bot, ctx.message)}play` to play new songs!")

        await ctx.send(embed = music_field)

    #@cog_ext.cog_slash(name="queue")
    @commands.command()
    async def queue(self, ctx):
        music_field = discord.Embed(colour = discord.Colour(0xFDED32))
        music_field.set_author(name = "𝓜𝓾𝓼𝓲𝓬")
        conn = sqlite.connect("data/internal.db")
        total_duration = 0
        if ctx.voice_client:
            if ctx.voice_client.is_playing or ctx.voice_client.is_paused():
                current_song = self.song_from_string(conn.execute("SELECT current_song FROM music WHERE guild_id = ?", (ctx.guild.id, )).fetchall()[0][0])
                songs = self.songs_from_string(conn.execute(f"SELECT queued_songs FROM music WHERE guild_id = {ctx.guild.id}").fetchall()[0][0])
                loop = "Yes" if conn.execute(f"SELECT loop FROM music WHERE guild_id = ?", (ctx.guild.id, )).fetchall()[0][0] == 1 else "No"
                music_field.title = f"`Now playing` - {current_song['title']}"
                if songs:
                    for song in songs:
                        author = await ctx.guild.fetch_member(song['author'])
                        music_field.add_field(name = f"`{songs.index(song) + 1}` - {song['title']} by `{song['artist']}`", value = f"Duration: `{datetime.timedelta(seconds = int(song['duration']))}` | Popularity: `{song['likes']}/{song['dislikes']}` | Requested by {author.mention}", inline = False)
                        total_duration += int(song['duration'])

                    music_field.add_field(name = f"Total Duration", value = f"`{datetime.timedelta(seconds = total_duration)}`")
                    music_field.add_field(name = f"Number of songs", value = f"`{len(songs)}`")
                    music_field.add_field(name = f"Loop", value = f"`{loop}`")

                else:
                    author = await ctx.guild.fetch_member(current_song['author'])
                    music_field.add_field(name = f"Author: `{current_song['artist']}`", value = f"Duration: `{datetime.timedelta(seconds = int(current_song['duration']))}` | Popularity: `{current_song['likes']}/{current_song['dislikes']}` | Requested by {author.mention}")

            else:
                music_field.add_field(name = f"They are no songs playing!", value = f"If you want to play a new song simply type `{get_prefix(self.bot, ctx.message)}play`")

            await ctx.send(embed = music_field)

    #@cog_ext.cog_slash(name="remove")
    @commands.command()
    async def remove(self, ctx, index):
        index = int(index)
        music_field = discord.Embed(colour = discord.Colour(0xFDED32))
        music_field.set_author(name = "𝓜𝓾𝓼𝓲𝓬")
        conn = sqlite.connect("data/internal.db")
        current_song = self.song_from_string(conn.execute("SELECT current_song FROM music WHERE guild_id = ?", (ctx.guild.id, )).fetchall()[0][0])
        songs = self.songs_from_string(conn.execute(f"SELECT queued_songs FROM music WHERE guild_id = {ctx.guild.id}").fetchall()[0][0])

        if not songs and not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
            music_field.add_field(name = "There is no existing queue", value = f"But you can use `{get_prefix(self.bot, ctx.message)}play` to play something!")

        elif index - 1 > len(songs):
            music_field.add_field(name = "This song doesn't exist in your queue", value = f"To remove all songs from the queue use `{get_prefix(self.bot, ctx.message)}stop`")

        elif index - 1 <= len(songs) and index - 1 >= 0:
            removed_song = songs.pop(index - 1)
            music_field.add_field(name = f"{removed_song['title']} has been removed from your queue!", value = f"I bet nobody will miss it anyway")
        conn.close()
        await ctx.send(embed = music_field)

    #@cog_ext.cog_slash(name="move")
    @commands.command()
    async def move(self, ctx, index_of_song, desired_position):
        music_field = discord.Embed(colour = discord.Colour(0xFDED32))
        music_field.set_author(name = "𝓜𝓾𝓼𝓲𝓬")
        index_of_song = int(index_of_song) - 1
        desired_position = int(desired_position) - 1
        conn = sqlite.connect("data/internal.db")
        current_song = self.song_from_string(conn.execute("SELECT current_song FROM music WHERE guild_id = ?", (ctx.guild.id, )).fetchall()[0][0])
        songs = self.songs_from_string(conn.execute(f"SELECT queued_songs FROM music WHERE guild_id = {ctx.guild.id}").fetchall()[0][0])
        if index_of_song >= 0 and desired_position >= 0:
            if index_of_song > len(songs):
                music_field.add_field(name = f"There is no song on position `{index_of_song + 1}`", value = f"Did you want to skip? Use `{get_prefix(bot, ctx.message)}skip` Don't worry, if you have loop enabled the song will stay in queue")

            else:
                if desired_position > len(songs) - 1:
                    songs.append(songs.pop(index_of_song))
                    conn.execute("UPDATE music SET queued_songs = ? WHERE guild_id = ?", (self.songs_to_string(songs), ctx.guild.id))
                    conn.commit()
                    music_field.add_field(name = f"Song `{songs[-1]['title']}` was moved to the end of queue from position `{index_of_song + 1}`", value = f"This happened because you entered number greater than the index of last song")
                
                else:
                    songs.insert(desired_position, songs.pop(index_of_song))
                    conn.execute("UPDATE music SET queued_songs = ? WHERE guild_id = ?", (self.songs_to_string(songs), ctx.guild.id))
                    conn.commit()
                    music_field.add_field(name = f"I have moved `{songs[desired_position]['title']}`from position `{index_of_song + 1}` to `{desired_position + 1}`", value = f"I hope I got it right!")

        conn.close()
        await ctx.send(embed = music_field)

    #@cog_ext.cog_slash(name="now")
    @commands.command()
    async def now(self, ctx):
        music_field = discord.Embed(colour = discord.Colour(0xFDED32))
        music_field.set_author(name = "𝓜𝓾𝓼𝓲𝓬")
        conn = sqlite.connect("data/internal.db")
        current_song = self.song_from_string(conn.execute("SELECT current_song FROM music WHERE guild_id = ?", (ctx.guild.id, )).fetchall()[0][0])
        conn.close()
        author = await ctx.guild.fetch_member(current_song['author'])
        music_field.title = f"`Now playing` - {current_song['title']}"
        music_field.add_field(name = f"Author: `{current_song['artist']}`", value = f"Duration: `{datetime.timedelta(seconds = int(current_song['duration']))}` | Popularity: `{current_song['likes']}/{current_song['dislikes']}` | Requested by {author.mention}")
        await ctx.send(embed = music_field)

    #@cog_ext.cog_slash(name="grab")
    @commands.command()
    async def grab(self, ctx):
        music_field = discord.Embed(colour = discord.Colour(0xFDED32))
        music_field.set_author(name = "𝓜𝓾𝓼𝓲𝓬")
        dm_field = discord.Embed(colour = discord.Colour(0xFDED32))
        dm_field.set_author(name = "𝓖𝓛𝓞𝓑")
        conn = sqlite.connect("data/internal.db")
        current_song = self.song_from_string(conn.execute("SELECT current_song FROM music WHERE guild_id = ?", (ctx.guild.id, )).fetchall()[0][0])
        conn.close()

        if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            music_field.title = f"{current_song['title']}"
            music_field.add_field(name = f"`{current_song['artist']}`", value = f"Artist")
            music_field.add_field(name = f"`{datetime.timedelta(seconds = int(current_song['duration']))}`", value = f"Total Duration")
            music_field.add_field(name = f"`{current_song['likes']}/{current_song['dislikes']}`", value = f"Popularity")
            music_field.add_field(name = f"You really liked it, didn't ya?", value = f"*I sent this song to your DMs*")
            dm_field.title = f"{current_song['title']}"
            dm_field.add_field(name = f"`{current_song['artist']}`", value = f"Artist")
            dm_field.add_field(name = f"`{datetime.timedelta(seconds = int(current_song['duration']))}`", value = f"Total Duration")
            dm_field.add_field(name = f"`{current_song['likes']}/{current_song['dislikes']}`", value = f"Popularity")
            dm_field.add_field(name = f"Here you go!", value = f"{current_song['link']}")
            channel = await ctx.author.create_dm()
            await channel.send(embed = dm_field)
             
        
        else:
            music_field.title = f"I'm not playing anything!"
            music_field.add_field(name = f"If I'm not playing anything what am I supposed to send you?", value = f"*Who's the ape now, huh.*")

        await ctx.send(embed = music_field)

    #@cog_ext.cog_slash(name="addToPlaylist")
    @commands.command()
    async def addToPlaylist(self, ctx, name, *, song_name = None):
        music_field = discord.Embed(colour = discord.Colour(0xFDED32))
        music_field.set_author(name = "𝓜𝓾𝓼𝓲𝓬")
        conn = sqlite.connect("data/internal.db")
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
                info = self.get_audio_info(song_name)
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

    #@cog_ext.cog_slash(name="updatePlaylist")
    @commands.command()
    async def updatePlaylist(self, ctx, name):
        music_field = discord.Embed(colour = discord.Colour(0xFDED32))
        music_field.set_author(name = "𝓜𝓾𝓼𝓲𝓬")
        conn = sqlite.connect("data/internal.db")
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

    #@cog_ext.cog_slash(name="playPlaylist")
    @commands.command()
    async def playPlaylist(self, ctx, name):
        music_field = discord.Embed(colour = discord.Colour(0xFDED32))
        music_field.set_author(name = "𝓜𝓾𝓼𝓲𝓬")
        conn = sqlite.connect("data/internal.db")
        if len(ctx.message.mentions) == 0:
            data = conn.execute(f"SELECT * FROM playlists WHERE name = '{name}'").fetchall()

        else:
            data = conn.execute(f"SELECT * FROM playlists WHERE name = '{name}' user_id = '{ctx.message.mentions[0].id}'").fetchall()

        if len(data) != 0:
            songs = data[0][3].split("||")
            user_id = data[0][1]
            songs_to_play = []
            for song in songs:
                song = song.split("|")
                for i in range(len(song) - 1):
                    if song[i] == "":
                        song.pop(i)
                songs_to_play.append(song)

            self.songs.clear
            if not ctx.voice_client:
                await ctx.author.voice.channel.connect()

            for song in songs_to_play:
                song_to_add = {'track': song[0], 'title': song[1], 'artist': song[2], 'duration': float(song[3]), 'likes': int(song[4]), 'dislikes': int(song[5]), 'author': ctx.guild.get_member(ctx.author.id)}
                self.songs.append(song_to_add)

            if not ctx.voice_client.is_playing() or not ctx.voice_client.is_paused():
                self.play_audio(ctx)

            music_field.add_field(name = f"Replaced your queue with songs from playlist `{name}`", value = f"If you add any songs to your queue, you can update your playlist using `{get_prefix(self.bot, ctx.message)}addToPlaylist {name} update`")

        else:
            music_field.add_field(name = f"I couldn't find any playlist under name `{name}`", value = f"Don't worry, you can always create a new one with this name using `{get_prefix(self.bot, ctx.message)}addToPlaylist {name} song`")

        conn.close()
        await ctx.send(embed = music_field)

# return {"track": info['entries'][0]['url'], "title": info['entries'][0]['title'], "artist": info['entries'][0]['creator'], "duration": info['entries'][0]['duration'], "likes": info['entries'][0]['like_count'], "dislikes": info['entries'][0]['dislike_count']}

    #@cog_ext.cog_slash(name="displayPlaylist")
    @commands.command()
    async def displayPlaylist(self, ctx, name):
        music_field = discord.Embed(colour = discord.Colour(0xFDED32))
        music_field.set_author(name = "𝓜𝓾𝓼𝓲𝓬")
        conn = sqlite.connect("data/internal.db")
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
    conn = sqlite.connect("data/internal.db")
    try:
        return conn.execute(f"SELECT * FROM prefixes WHERE guild_id = {message.guild.id}").fetchall()[0][2]
    except:
        conn.execute(f"INSERT INTO prefixes VALUES(NULL, ?, ?)", (message.guild.id, "."))
        conn.commit()
        return conn.execute(f"SELECT * FROM prefixes WHERE guild_id = {message.guild.id}").fetchall()[0][2]

    conn.close()