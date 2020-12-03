import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
import sqlite3 as sqlite
import random as random

class _help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx, spec = None):
        prefix = get_prefix(self.bot, ctx.message)
        help_field = discord.Embed(colour = discord.Colour(0xFDED32))
        help_field.set_author(name = "𝓗𝓮𝓵𝓹")

        if spec == None:
            help_field.title = f"Essentials"
            help_field.add_field(name = f"{prefix}ping", value = "Return pong with your servers name!", inline = False)
            help_field.add_field(name = f"{prefix}changePrefix", value = "Changes the prefix for this server.", inline = False)
            await ctx.send(embed = help_field)

            help_field = discord.Embed(colour = discord.Colour(0xFDED32))
            help_field.set_author(name = "𝓗𝓮𝓵𝓹")
            help_field.title = f"Kicks and Bans"
            help_field.add_field(name = f"{prefix}voteKick", value = "Let the democracy decide if some user should be kicked!", inline = False)
            help_field.add_field(name = f"{prefix}resetVoteKick", value = "Stop the current voting on kicking", inline = False)
            help_field.add_field(name = f"{prefix}voteBan", value = "Should someone be banned? Let the Senate decide his fate.", inline = False)
            help_field.add_field(name = f"{prefix}resetVoteBan", value = "You changed your mind? Don't worry, you can reset ban voting.", inline = False)
            await ctx.send(embed = help_field)

            help_field = discord.Embed(colour = discord.Colour(0xFDED32))
            help_field.set_author(name = "𝓗𝓮𝓵𝓹")
            help_field.title = f"Citations"
            help_field.add_field(name = f"{prefix}writeThatDown", value = "Someone said something life-changing or particulary funny? Let me remember that!", inline = False)
            help_field.add_field(name = f"{prefix}whatDidYouSay", value = "You want to read something funny that other said? I gotchya.", inline = False)
            await ctx.send(embed = help_field)

            help_field = discord.Embed(colour = discord.Colour(0xFDED32))
            help_field.set_author(name = "𝓗𝓮𝓵𝓹")
            help_field.title = f"Hangman"
            help_field.add_field(name = f"{prefix}hangmanStart", value = "Starts new hangman game session on your server!", inline = False)
            help_field.add_field(name = f"{prefix}hangmanGuess", value = "Take a guess in your current hangman session, and don't let yourself to be.. Hanged?", inline = False)
            help_field.add_field(name = f"{prefix}hangmanDelete", value = "Deletes current session of hangman if you don't want to play anymore or you want to start a new one", inline = False)
            await ctx.send(embed = help_field)

            help_field = discord.Embed(colour = discord.Colour(0xFDED32))
            help_field.set_author(name = "𝓗𝓮𝓵𝓹")
            help_field.title = f"Role and nickname managment"
            help_field.add_field(name = f"{prefix}addRole", value = "Create roles quickly using this command, with random color gen and predefined permissions!", inline = False)
            help_field.add_field(name = f"{prefix}deleteRole", value = "You don't want particular role to exist? Delete it.", inline = False)
            help_field.add_field(name = f"{prefix}assignRole", value = "Some users out of their boundaries or screaming to be managed into some role? Use this command!", inline = False)
            help_field.add_field(name = f"{prefix}changeNickname", value = "Quickly change or delete nicknames of user on your server!", inline = False)
            await ctx.send(embed = help_field)

            help_field = discord.Embed(colour = discord.Colour(0xFDED32))
            help_field.set_author(name = "𝓗𝓮𝓵𝓹")
            help_field.title = f"Music"
            help_field.add_field(name = f"{prefix}join", value = "Want some friend in you voice channel? No problem, I'll join.", inline = False)
            help_field.add_field(name = f"{prefix}leave", value = "Oh.. So.. You don't need me anymore?", inline = False)
            help_field.add_field(name = f"{prefix}play", value = "If you want to jam to something, I'm the right person to ask.", inline = False)
            help_field.add_field(name = f"{prefix}pause", value = "Somebody knocked on the door or is just generally annoying you while you listen to music? I got'ya", inline = False)
            help_field.add_field(name = f"{prefix}resume", value = "When the time is right, you can resume your music and continue jammin'!", inline = False)
            help_field.add_field(name = f"{prefix}skip", value = "You don't like the song that's playing right now? Skip it!", inline = False)
            help_field.add_field(name = f"{prefix}stop", value = "Awful sounds coming from that bots mouth, I need to stop it!", inline = False)
            help_field.add_field(name = f"{prefix}loop", value = "If you are really feeling the current song or queue you can loop it.", inline = False)
            help_field.add_field(name = f"{prefix}remove", value = "Remove a specific song from your current queue", inline = False)
            help_field.add_field(name = f"{prefix}queue", value = "Display your current list of added songs!", inline = False)
            help_field.add_field(name = f"𝙉𝙚𝙚𝙙 𝙢𝙤𝙧𝙚 𝙞𝙣𝙛𝙤?", value = f"𝘛𝘺𝘱𝘦 {prefix}help `command` 𝘵𝘰 𝘨𝘦𝘵 𝘥𝘦𝘵𝘢𝘪𝘭𝘦𝘥 𝘥𝘦𝘴𝘤𝘳𝘪𝘱𝘵𝘪𝘰𝘯", inline = False)
            await ctx.send(embed = help_field)
        #_______________________________________________________________________________________________________________________________________________________________________________________________________________________________________

        elif spec.lower() == "kick" or spec.lower() == "votekick":
            help_field.add_field(name = f"{prefix}voteKick `@user` `number`", value = f"Takes one obligatory argument that specifies whom to kick `@user` and one optional that sets the number of required votes for the kick to happen `number`. \n Also summonable by `{prefix}vk`, `{prefix}votek`")
            help_field.add_field(name = f"{prefix}resetVoteKick `@user`", value = f"Resets the voting against a specific member `@user` if provided or resets all voting on server if you don't mention anybody. \n Works also by typing `{prefix}rvk`, `{prefix}resetvk`")
            await ctx.send(embed = help_field)

        elif spec.lower() == "ban" or spec.lower() == "voteban":
            help_field.add_field(name = f"{prefix}voteBan `@user` `number`", value = f"One required argument `@user` determinates person to start vote against and one optional that sets the number of required votes for the kick to happen `number`. \n Also summonable by `{prefix}vb`, `{prefix}voteb`")
            help_field.add_field(name = f"{prefix}resetVoteBan `@user`", value = f"Resets the voting against a specific member `@user` if provided or resets all voting on server if you don't mention anybody. \n Works also by typing `{prefix}rvb`, `{prefix}resetvb`")
            await ctx.send(embed = help_field)

        elif spec.lower() == "cite" or spec.lower() == "whatdidyousay" or spec.lower() == "writethatdown" or spec.lower() == "citeit":
            help_field.add_field(name = f"{prefix}writeThatDown `sentence` `@user` `name`", value = f"Required argument `sentence` is thing that you want to save while `@user` determinates person that said it. And `name` is used to save it under specific name, this can be ommited. \n Can also be summoned by `{prefix}wtd`, `{prefix}citeit`")
            help_field.add_field(name = f"{prefix}whatDidYouSay `@user` `name`", value = f"Here `@user` is volutary and when given, this command will return random quote from that user. When both `@user` and `name` are given it will return specific quote that was saved with that name. When none of these are given, random quote from anybody on server is selected. \n Command also under `{prefix}wdys`, `{prefix}cite`")
            await ctx.send(embed = help_field)

        elif spec.lower() == "hangman" or spec.lower() == "hangmanstart" or spec.lower() == "hangmanguess" or spec.lower() == "hangmandelete" or spec.lower() == "hangmanaddword":
            help_field.add_field(name = f"{prefix}hangmanStart `word` `number`", value = f"If `word` is given this command will return a new game of hangman with that `word`, and if voluntary argument `number` given too it will determinate max number of wrong tries. If none of these are given, hangman will select a random word from database \n Works by typing `{prefix}hs`, `{prefix}hangmanS`")
            help_field.add_field(name = f"{prefix}hangmanGuess `letter`", value = f"You have to type `letter` as an argument, if word in current word in game of hangman contains that word, it gets completed into it, if not you get one wrong try \n Summonable by `{prefix}h`, `{prefix}hangmanG`")
            help_field.add_field(name = f"{prefix}hangmanDelete", value = f"Takes 0 arguments and it deletes current game of hangman \n You can type `{prefix}hd`, `{prefix}hstop`")
            help_field.add_field(name = f"{prefix}hangmanAddWord `word` `number`", value = f"Here argument `word` is obligatory and it should be the word you want to add to the databank of the hangman. While `number` is optional and it's the number of max wrong tries for this word. \n Command also works by typing `{prefix}haw`, `{prefix}hangmanAW`")
            await ctx.send(embed = help_field)

        elif spec.lower() == "addrole" or spec.lower() == "deleterole" or spec.lower() == "role" or spec.lower() == "assignrole":
            help_field.add_field(name = f"{prefix}addRole `name` `color` `permissions`", value = f"This command purpose is to create roles efficiently. `name` is needed and it's the name of the role. `color` is optional and you can choose between 'yellow', 'orange', 'red', 'jungle', 'pine', 'steel', 'sappire', 'navy', 'electric', 'magenta', 'pink' or 'random', random one will be generated. And lastly with `permissions` you can choose between predefined ones: 'general', 'administrator', if none given 'general' will be used \n Summonable by `{prefix}addr`, `{prefix}aRole`")
            help_field.add_field(name = f"{prefix}deleteRole `@role`", value = f"Deletes the given `@role` and this argument is obligatory. \n Works also by typing `{prefix}delr`, `{prefix}dRole`")
            help_field.add_field(name = f"{prefix}assignRole `@role` `@users`", value = f"Adds all `@users` to provided `@role`. Both of those arguments are necessary \n Works also by typing `{prefix}assR`, `{prefix}asRole`")
            await ctx.send(embed = help_field)

        elif spec.lower() == "ping" or spec.lower() == "changeprefix":
            help_field.add_field(name = f"{prefix}ping", value = f"This command takes zero arguments. It will return Pong with name of your server and latency")
            help_field.add_field(name = f"{prefix}changePrefix `word`", value = f"This will change prefix on your server for this bot. Argument `word` is needed and it can be almost any character, word or sequence of characters \n Works also by typing `{prefix}cp`, `{prefix}cPrefix`, `{prefix}GlobChangePrefix`")
            help_field.add_field(name = f"globPrefix", value = f"Zero argument command that doesn't require you to type prefix. It's used to determinate what prefix is GLOB set on")
            await ctx.send(embed = help_field)

        elif spec.lower() == "nick" or spec.lower() == "changenick" or spec.lower() == "changenickname":
            help_field.add_field(name = f"changeNickname `nickname` `@users`", value = f"With this command you can quickly change nicknames of users. Takes 2 arguments. First `nickname` nickname that you want to change to and if ommited this command will erase users nick. `users` Needed argument that determinates what users should receive nickname or get nick erased. \n Works also by typing `{prefix}cn`, `{prefix}cNick`")
            await ctx.send(embed = help_field)

        elif spec.lower() == "music" or spec.lower() == "join" or spec.lower() == "play" or spec.lower() == "pause" or spec.lower() == "stop" or spec.lower() == "play" or spec.lower() == "leave" or spec.lower() == "loop" or spec.lower() == "remove" or spec.lower() == "queue" or spec.lower() == "skip":
            help_field.add_field(name = f"{prefix}join", value = f"You have to be in a voice channel to issue this command. GLOB will then join your voice channel.") # \n Works also by typing `{prefix}cn`, `{prefix}cNick`")
            help_field.add_field(name = f"{prefix}leave", value = f"If you don't want glob to be in your channel anymore you can disconnect him from your channel") # \n Works also by typing `{prefix}cn`, `{prefix}cNick`")
            help_field.add_field(name = f"{prefix}play `song`", value = f"Takes one obligatory argument `song` which should be either youtube url or your search query") # \n Works also by typing `{prefix}cn`, `{prefix}cNick`")
            help_field.add_field(name = f"{prefix}pause", value = f"Requires zero arguments and it will pause your current song. If there is no song to be pause, nothing happens") # \n Works also by typing `{prefix}cn`, `{prefix}cNick`")
            help_field.add_field(name = f"{prefix}resume", value = f"No value needed. This will resume song if any was paused if no song is paused GLOB will only notify you") # \n Works also by typing `{prefix}cn`, `{prefix}cNick`")
            help_field.add_field(name = f"{prefix}stop", value = f"This argument will stop playing song and will purge entire queue if any queued songs exist. Use careful, no way of going back") # \n Works also by typing `{prefix}cn`, `{prefix}cNick`")
            help_field.add_field(name = f"{prefix}skip", value = f"GLOB will stop playing your current song. If queue exists the next song will be played. If queue is looped the skiped song will remain in queue") # \n Works also by typing `{prefix}cn`, `{prefix}cNick`")
            help_field.add_field(name = f"{prefix}remove `number`", value = f"If queue exist remove will take obligatory argument `number` and will remove the song from queue even if loop is set to True.") # \n Works also by typing `{prefix}cn`, `{prefix}cNick`")
            help_field.add_field(name = f"{prefix}queue", value = f"Information command that will provide you with list of current playing song and all the songs in queue and their order numbers in queue. If no queue exists it will only provide you info about the current song") # \n Works also by typing `{prefix}cn`, `{prefix}cNick`")
            await ctx.send(embed = help_field)

def setup(bot):
    bot.add_cog(_help(bot))

def get_prefix(bot, message):
    conn = sqlite.connect("internal.db")
    try:
        return conn.execute(f"SELECT * FROM prefixes WHERE guild_id = {message.guild.id}").fetchall()[0][2]
    except:
        conn.execute(f"INSERT INTO prefixes VALUES(NULL, ?, ?)", (message.guild.id, "."))
        conn.commit()
        return conn.execute(f"SELECT * FROM prefixes WHERE guild_id = {message.guild.id}").fetchall()[0][2]

    conn.close()