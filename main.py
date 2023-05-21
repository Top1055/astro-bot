import discord
from discord.ext import commands
import config
import help

cogs = []

class Serenity(commands.Bot):

    # Once the bot is up and running
    async def on_ready(self):
        # Set the status
        await self.change_presence(activity=config.get_status())

        # Setup commands
        for cog in cogs:
            await cog.setup(self)

client = Serenity(command_prefix=config.get_prefix(), intents=discord.Intents.all())
client.help_command = help.AstroHelp()

client.run(config.get_login("dev"))
