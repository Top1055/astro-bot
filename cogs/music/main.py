import discord
from discord.ext import commands
from discord.ext.commands.context import Context
import cogs.music.util as util
import cogs.music.queue as queue

import datetime
import pytz

import yt_dlp

from cogs.music.help import music_help

ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
}

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

    
    @commands.command(
            help="Leaves the voice chat if the bot is present",
            aliases=['disconnect'])
    async def leave(self, ctx: Context):
        await util.leave_vc(ctx)
        await ctx.message.add_reaction('👍')


    @commands.command(
            help="Queues a song into the bot",
            aliases=['p', 'qeue', 'q'])
    async def play(self, ctx: Context, *, url=None):
        if url is None:
            raise commands.CommandError("Must provide a link or search query")


        await util.join_vc(ctx)


        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        ctx.voice_client.play(discord.FFmpegPCMAudio(executable="ffmpeg", source=filename), after=self.test)


    def test(self, error):
        print("Hello")
