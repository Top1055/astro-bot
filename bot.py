from discord.ext import commands
import config
from cogs.music.main import music

cogs = [
        music
        ]

class Astro(commands.Bot):

    # Once the bot is up and running
    async def on_ready(self):
        # Set the status
        await self.change_presence(activity=config.get_status())

        # Setup commands
        for cog in cogs:
            await self.add_cog(cog(self))
