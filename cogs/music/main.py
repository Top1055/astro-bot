import discord
from discord.ext import commands
from discord.ext.commands.context import Context
import cogs.music.util as util

import datetime
import pytz

from cogs.music.help import music_help

class music(commands.Cog):
    def __init__(self, client):
        self.client = client

        self.name = "🎶 Music"
        self.emoji = "🎶"

        help_command = music_help()
        help_command.cog = self
        self.help_command = help_command

    @commands.command(
            help="Displays latency from the bot",
            aliases=['delay'])
    async def ping(self, ctx: Context):
        start_time = datetime.datetime.now(pytz.utc)
        end_time = ctx.message.created_at

        delay = int((end_time - start_time).total_seconds() * 1000)

        await ctx.send(f"Pong! `{delay}MS`")


    @commands.command(
            help="Connects to your current voice channel",
            aliases=['connect'])
    async def join(self, ctx: Context):
        await util.join_vc(ctx)
        await ctx.message.add_reaction('👍')


