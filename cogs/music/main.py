from discord.ext import commands
from discord.ext.commands.context import Context

import cogs.music.util as util
import cogs.music.queue as queue
import cogs.music.translate as translate

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

        queue.initialize_tables()


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
    @commands.check(util.in_server)
    async def play(self, ctx: Context, *, url=None):
        if url is None:
            raise commands.CommandError("Must provide a link or search query")

        server = ctx.guild.id

        #TODO potentially save requests before getting stream link
        audio = translate.main(url)

        #TODO make sure user isn't queuing in dm for some stupid reason
        for song in audio:
           await queue.add_song(server, song, ctx.author.id)

        await ctx.message.add_reaction('👍')

        await util.join_vc(ctx)

        if await queue.is_server_playing(ctx.guild.id):
            return

        await queue.update_server(server, True)
        await queue.play(ctx)
