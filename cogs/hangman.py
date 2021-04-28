import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
import sqlite3 as sqlite
import random as random

class hangman(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name = "hangmanGuess", aliases = ["hG", "hg", "h", "hangmanG", "HG"])
    async def hangmanGuess(self, ctx, letter):
        conn = sqlite.connect("data/internal.db")
        letter = letter.lower()
        hangman_guess_field = discord.Embed(colour = discord.Colour(0xFDED32))
        hangman_guess_field.set_author(name = "𝓗𝓪𝓷𝓰𝓶𝓪𝓷")

        if len(conn.execute(f"SELECT * FROM hangmans WHERE guild_id = '{ctx.guild.id}'").fetchall()) == 0:
            hangman_guess_field.add_field(name = f"There is no game of hangman going on right now!", value = f"Don't be shy, {ctx.author.mention}. Start a new one using `{get_prefix(self.bot, ctx.message)}hangmanStart`", inline = False)
            await ctx.send(embed = hangman_guess_field)

        else:
            data = conn.execute(f"SELECT * FROM hangmans WHERE guild_id = '{ctx.guild.id}'").fetchall()

            word = data[0][2]
            current_tries = data[0][3]
            tries_max = data[0][4]
            guessed_word = list(data[0][5])
            print_word = ""
            indexes = [i for i, j in enumerate(list(word)) if j == letter]

            if letter in guessed_word:
                hangman_guess_field.add_field(name = f"You guessed this letter already!", value = f"But don't worry, {ctx.author.mention}. I'll take no tries from you.", inline = False)
                await ctx.send(embed = hangman_guess_field)

            else:
                if len(indexes) == 0 and current_tries + 1 != tries_max:
                    for i in range(len(guessed_word) - 1):
                        print_word += f"`{guessed_word[i]}` "

                    print_word += f"`{guessed_word[-1]}`"  
                    current_tries += 1
                    conn.execute(f"UPDATE hangmans SET current_tries = '{current_tries}' WHERE guild_id = '{ctx.guild.id}'")
                    conn.commit()
                    hangman_guess_field.add_field(name = f"{print_word}", value = f"You got it wrong! Don't worry, you still have `{tries_max - (current_tries)}` tries", inline = False)
                    await ctx.send(embed = hangman_guess_field)

                elif len(indexes) == 0 and current_tries + 1 >= tries_max:

                    for i in range(len(list(word)) - 1):
                        print_word += f"`{word[i]}` "

                    print_word += f"`{word[-1]}`"  

                    conn.execute(f"DELETE FROM hangmans WHERE guild_id = '{ctx.guild.id}'")
                    conn.commit()
                    hangman_guess_field.add_field(name = f"{print_word}", value = f"You didn't get it, good luck next time!", inline = False)
                    await ctx.send(embed = hangman_guess_field)

                elif len(indexes) > 0:
                    for index in indexes:
                        guessed_word[index] = word[index]

                    print_word = ""

                    for i in range(len(guessed_word) - 1):
                        print_word += f"`{guessed_word[i]}` "

                    print_word += f"`{guessed_word[-1]}`"  
                    guessed_word = "".join(guessed_word)

                    if guessed_word == word:
                        conn.execute(f"DELETE FROM hangmans WHERE guild_id = '{ctx.guild.id}'")
                        conn.commit()
                        hangman_guess_field.add_field(name = f"{print_word}", value = f"You got it! Well done {ctx.author.mention}", inline = False)
                        await ctx.send(embed = hangman_guess_field)

                    else:
                        conn.execute(f"UPDATE hangmans SET guessed_word = '{guessed_word}' WHERE guild_id = '{ctx.guild.id}'")
                        conn.commit()
                        hangman_guess_field.add_field(name = f"{print_word}", value = f"They see {ctx.author.mention} rollin'. Onto the next letter!", inline = False)
                        await ctx.send(embed = hangman_guess_field)
        conn.close()

    @commands.command(name = "hangmanStart", aliases = ["hS", "hs", "hangmanS", "HS", "hangmans"])
    async def hangmanStart(self, ctx, word = None, max_tries = 10):
        conn = sqlite.connect("data/internal.db")
        hangman_start_field = discord.Embed(colour = discord.Colour(0xFDED32))
        hangman_start_field.set_author(name = "𝓗𝓪𝓷𝓰𝓶𝓪𝓷")
        guessed_word = ""
        print_word = ""

        if word == None:
            wordList = conn.execute(f"SELECT * FROM hangman_word_list").fetchall()
            word_index = random.randrange(len(wordList))
            word = wordList[word_index][1]
            max_tries = wordList[word_index][2]
        else:
            word= word.replace("'", "").replace(" ", "").replace(",", "")
            await ctx.message.delete()

        if len(conn.execute(f"SELECT * FROM hangmans WHERE guild_id = '{ctx.guild.id}'").fetchall()) != 0:
            hangman_start_field.add_field(name = f"There is game of hangman going on already!", value = f"Try and guess using `{get_prefix(self.bot, ctx.message)}hangmanGuess`", inline = False)
            await ctx.send(embed = hangman_start_field)

        else:
            for i in range(len(list(word))):
                guessed_word += "_"

            for i in range(len(list(word)) - 1):
                print_word += "`_` "

            print_word += "`_`"

            conn.execute(f"INSERT INTO hangmans VALUES(NULL, ?, ?, ?, ?, ?)", (ctx.guild.id, word, 0, max_tries, guessed_word))
            conn.commit()

            hangman_start_field.add_field(name = f"{print_word}", value = f"New game of hangman started by {ctx.author.mention}! \n Max number of wrong tries is set to `{max_tries}`")
            await ctx.send(embed = hangman_start_field)
        conn.close()


    @commands.command(name = "hangmanDelete", aliases = ["hD", "hd", "hstop", "hangmanD", "HD"])
    async def hangmanDelete(self, ctx):
        conn = sqlite.connect("data/internal.db")
        hangman_delete_field = discord.Embed(colour = discord.Colour(0xFDED32))
        hangman_delete_field.set_author(name = "𝓗𝓪𝓷𝓰𝓶𝓪𝓷")

        if len(conn.execute(f"SELECT * FROM hangmans WHERE guild_id = '{ctx.guild.id}'").fetchall()) == 0:
            hangman_delete_field.add_field(name = f"There is no game of hangman going on right now!", value = f"But you can start a new one using `{get_prefix(self.bot, ctx.message)}hangmanStart`", inline = False)
            await ctx.send(embed = hangman_delete_field)

        else:
            conn.execute(f"DELETE from hangmans WHERE guild_id = {ctx.guild.id}")
            conn.commit()
            hangman_delete_field.add_field(name = f"Deleted current game of hangman", value = f"Be sure to play it again! `{get_prefix(self.bot, ctx.message)}hangmanStart` to start", inline = False)
            await ctx.send(embed = hangman_delete_field)
        conn.close()
            
    @commands.command(name = "hangmanAddWord", aliases = ["haw", "hangmanAW", "hangmanaw"])
    async def hangmanAddWord(self, ctx, word, max_tries = 5):
        conn = sqlite.connect("data/internal.db")
        word = word.replace("'", "").replace(" ", "").replace(",", "")
        wordList = conn.execute(f"SELECT * FROM hangman_word_list").fetchall()[0]
        hangman_add_field = discord.Embed(colour = discord.Colour(0xFDED32))
        hangman_add_field.set_author(name = "𝓗𝓪𝓷𝓰𝓶𝓪𝓷")
        if word in wordList:
            hangman_add_field.add_field(name = f"{word} is already in database!", value = f"If you want others to guess this specific word try `{get_prefix(self.bot, ctx.message)}hangmanStart {word}` to start", inline = False)
            await ctx.send(embed = hangman_add_field)
        else:
            conn.execute(f"INSERT INTO hangman_word_list VALUES(NULL, ?, ?)", (word, max_tries))
            hangman_add_field.add_field(name = f"Added '{word}' into database with {max_tries} max wrong tries!", value = f"Thanks for contributing, {ctx.author.mention}.", inline = False)
            await ctx.send(embed = hangman_add_field)

        conn.close()

def setup(bot):
    bot.add_cog(hangman(bot))

def get_prefix(bot, message):
    conn = sqlite.connect("data/internal.db")
    try:
        return conn.execute(f"SELECT * FROM prefixes WHERE guild_id = {message.guild.id}").fetchall()[0][2]
    except:
        conn.execute(f"INSERT INTO prefixes VALUES(NULL, ?, ?)", (message.guild.id, "."))
        conn.commit()
        return conn.execute(f"SELECT * FROM prefixes WHERE guild_id = {message.guild.id}").fetchall()[0][2]

    conn.close()