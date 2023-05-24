from collections.abc import Mapping
from typing import List
import discord
from discord.app_commands import Command
from discord.ext import commands
from discord.ext.commands.cog import Cog
import config

class AstroHelp(commands.MinimalHelpCommand):

    def __init__(self):
        super().__init__()
        self.command_attrs = {
                'name': "help",
                'aliases': ["commands", "?"],
                'cooldown': commands.CooldownMapping.from_cooldown(2, 5.0, commands.BucketType.user)
                }


    # Called when using help no args
    async def send_bot_help(self, mapping: Mapping[Cog, List[Command]]):

        # Our embed message
        embed = discord.Embed(
                title="Help",
                color=config.get_color("main"))
        embed.add_field(name="",
                        value="Use `help <command>` or `help <category>` for more details",
                        inline=False)

        embed.set_footer(text=f"Prefix: {self.context.prefix}")

        # grabs iterable of (Cog, list[Command])
        for cog, commands in mapping.items():
            
            # Grab commands only the user can access
            # Safe to ignore warning
            filtered = await self.filter_commands(commands, sort=True)

            # For each command we grab the signature
            command_signatures = [
                    # Rmove prefix and format command name
                    f"``{self.get_command_signature(c)[1:]}``" for c in filtered]

            # Check if cog has any commands
            if command_signatures:

                # Use get incase cog is None
                cog_name = getattr(cog, "name", "No Category")

                # Add cog section to help message
                embed.add_field(
                        name=f"{cog_name}",
                        value="\n".join(command_signatures),
                        inline=True)

        # Display message
        channel = self.get_destination()
        await channel.send(embed=embed)


    # Help for specific command
    async def send_command_help(self, command):

        embed = discord.Embed(
                title=self.get_command_signature(command)[1:],
                color=config.get_color("main"))
        embed.set_footer(text=f"Prefix: {self.context.prefix}")
        embed.add_field(name="Description", value=command.help)

        alias = command.aliases
        if alias:
            embed.add_field(name="Aliases", value=", ".join(alias), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

# TODO add error support see
# https://gist.github.com/InterStella0/b78488fb28cadf279dfd3164b9f0cf96
# and
# https://gist.github.com/EvieePy/7822af90858ef65012ea500bcecf1612
