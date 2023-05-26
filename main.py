import discord
from bot import Astro
import config
import help

client = Astro(command_prefix=config.get_prefix(), intents=discord.Intents.all())
client.help_command = help.AstroHelp()

client.run(config.get_login("live"))
