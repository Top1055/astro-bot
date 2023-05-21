import discord
from discord.ext import commands

class AstroHelp(commands.HelpCommand):

    # Help regular
    async def send_bot_help(self, mapping):
        await self.context.send("This is help")


    # Help with specific command
    async def send_command_help(self, command):
        await self.context.send(f"You asked for help with: {command}")


    # Help for a group
    async def send_group_help(self, group):
        await self.context.send(f"This is a group: {group}")


    # Help for cog
    async def send_cog_help(self, cog):
        await self.context.send(f"This is a cog: {cog}")
