import discord
from discord.ext import commands
from discord.ext.commands.context import Context

import datetime
import pytz

class music(commands.Cog):
    def __init__(self, client):
        self.name = "🎶 Music"
        self.emoji = "🎶"
        self.client = client

    @commands.command(
            help="Displays latency from the bot",
            aliases=['delay'])
    async def ping(self, e: Context):
        start_time = datetime.datetime.now(pytz.utc)
        end_time = e.message.created_at

        delay = int((end_time - start_time).total_seconds() * 1000)

        await e.send(f"Pong! `{delay}MS`")
