import discord
from discord import Client
from discord.ext import commands
from discord.utils import get
from discord.ext.commands import has_permissions
import sqlite3 as sqlite
import random as random

class roleManagment(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.general_permissions = ["general", "administrator"]
        self.valid_permissions = ["create_instant_invite", "kick_members", "ban_members", "manage_channels", "manage_guild", "add_reactions", "stream", "mention_everyone", "manage_roles", "manage_nicknames", "manage_emojis"]

    @commands.command(name = "addRole", aliases = ["addR", "addr", "aRole"])
    async def addRole(self, ctx, role_name, color = None, *permissions):
        add_role_field = discord.Embed(colour = discord.Colour(0xFDED32))
        add_role_field.set_author(name = "𝓡𝓸𝓵𝓮 𝓶𝓪𝓷𝓪𝓰𝓶𝓮𝓷𝓽")

        if len(permissions) == 0:
            permissions = ["general"]

        if color == None or color.lower() == "random":
            color = int("%06x" % random.randint(0, 0xFFFFFF), 16)

        else:
            if color.lower() == "yellow":
                color = 0xFDED32

            elif color.lower() == "orange":
                color = 0xFF6600
            
            elif color.lower() == "red":
                color = 0xFF3300

            elif color.lower() == "jungle":
                color = 0x77B300

            elif color.lower() == "pine":
                color = 0x00CC99

            elif color.lower() == "steel":
                color = 0x4683B7

            elif color.lower() == "sappire":
                color = 0x1035AC

            elif color.lower() == "navy":
                color = 0x000080

            elif color.lower() == "electric":
                color = 0x8F00FF

            elif color.lower() == "magenta":
                color = 0x800080

            elif color.lower() == "pink":
                color = 0xFF33CC

            elif color.lower().startswith("<@"):
                color = int("%06x" % random.randint(0, 0xFFFFFF), 16)
            else:
                add_role_field.add_field(name = f"Invalid color entered! Using random color.", value = f"Supported colors are: `yellow`, `orange`, `red`, `jungle`, `pine`, `steel`, `sappire`, `navy`, `electric`, `magenta`, `pink`")
                await ctx.send(embed = add_role_field)
                color = int("%06x" % random.randint(0, 0xFFFFFF), 16)

        if len(permissions) != 0:
            for permission in permissions:
                if permission == "administrator":
                    await ctx.guild.create_role(name = role_name, colour = discord.Colour(color), permissions = discord.Permissions(administrator = True))
                    role = get(ctx.guild.roles, name = role_name)
                    add_role_field.add_field(name = f"New role named `{role}` created!", value = f"Everybody say thanks to {ctx.author.mention} for keeping everything managed!")
                    for member in ctx.message.mentions:
                        await member.add_roles(role)
                        add_role_field.add_field(name = f"User added to role!", value = f"{member.mention} is now part of {role.mention}")
                    await ctx.send(embed = add_role_field)
                    break
                elif permission in self.general_permissions:
                    await ctx.guild.create_role(name = role_name, colour = discord.Colour(color), permissions = discord.Permissions(104328768))
                    role = get(ctx.guild.roles, name = role_name)
                    add_role_field.add_field(name = f"New role named `{role}` created!", value = f"Everybody say thanks to {ctx.author.mention} for keeping everything managed!")
                    for member in ctx.message.mentions:
                        await member.add_roles(role)
                        add_role_field.add_field(name = f"User added to role!", value = f"{member.mention} is now part of {role.mention}")
                    await ctx.send(embed = add_role_field)
                    break

    @commands.command(name = "deleteRole", aliases = ["delR", "delr", "dRole"])
    async def deleteRole(self, ctx, role: discord.Role):
        role_id = role.id
        role_name = role.name
        delete_role_field = discord.Embed(colour = discord.Colour(0xFDED32))
        delete_role_field.set_author(name = "𝓡𝓸𝓵𝓮 𝓶𝓪𝓷𝓪𝓰𝓶𝓮𝓷𝓽")
        await role.delete()
        if get(ctx.guild.roles, name = role_id) == None:
            delete_role_field.add_field(name = f"Role `{role_name}` deleted!", value = f"Nobody liked them anyways..")
        else:
            delete_role_field.add_field(name = f"Couldn't delete that role!", value = f"They are putting bigger fight than we thought they would!")

        await ctx.send(embed = delete_role_field)

    @commands.command(name = "assignRole", aliases = ["assR", "asRole"])
    async def assignRole(self, ctx, role: discord.Role):
        assign_role_field = discord.Embed(colour = discord.Colour(0xFDED32))
        assign_role_field.set_author(name = "𝓡𝓸𝓵𝓮 𝓶𝓪𝓷𝓪𝓰𝓶𝓮𝓷𝓽")

        if len(ctx.message.mentions) == 0:
            assign_role_field.add_field(name = f"You have to mention users that you want to add!", value = f"You know.. Mention.. That thing with `@`")
            await ctx.send(embed = assign_role_field)
        else:
            for member in ctx.message.mentions:
                await member.add_roles(role)
                assign_role_field.add_field(name = f"User added to role!", value = f"{member.mention} is now part of {role.mention}")
            await ctx.send(embed = assign_role_field)
        
        
        
def setup(bot):
    bot.add_cog(roleManagment(bot))

def get_prefix(bot, message):
    conn = sqlite.connect("internal.db")
    try:
        return conn.execute(f"SELECT * FROM prefixes WHERE guild_id = {message.guild.id}").fetchall()[0][2]
    except:
        conn.execute(f"INSERT INTO prefixes VALUES(NULL, ?, ?)", (message.guild.id, "."))
        conn.commit()
        return conn.execute(f"SELECT * FROM prefixes WHERE guild_id = {message.guild.id}").fetchall()[0][2]

    conn.close()