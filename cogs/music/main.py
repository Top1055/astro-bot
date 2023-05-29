from discord.ext import commands
from discord.ext.commands.context import Context

import cogs.music.util as util
import cogs.music.queue as queue
import cogs.music.translate as translate

import datetime
import pytz
import asyncio

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
            aliases=['p'])
    async def play(self, ctx: Context, *, url=None):
        if url is None:
            raise commands.CommandError("Must provide a link or search query")
        elif ctx.guild is None:
            raise commands.CommandError("Command must be issued in a server")

        server = ctx.guild.id

        await ctx.message.add_reaction('👍')
        await util.join_vc(ctx)

        msg = await ctx.send("Fetching song(s)...")
        async with ctx.typing():
            #TODO potentially save requests before getting stream link
            # Grab video details such as title thumbnail duration
            audio = translate.main(url)

        await msg.delete()

        if len(audio) == 0:
            await ctx.message.add_reaction('🚫')
            await ctx.send("Failed to find song!")
            return


        #TODO make sure user isn't queuing in dm for some stupid reason
        for song in audio:
           song['position'] = await queue.add_song(
                   server,
                   song,
                   ctx.author.display_name)

        await util.queue_message(ctx, audio[0])


        if await queue.is_server_playing(server):
            return

        await queue.update_server(server, True)
        await queue.play(ctx)



    @commands.command(
            help="Display the current music queue",
            aliases=['q', 'songs'])
    async def queue(self, ctx: Context):

        server = ctx.guild

        # Perform usual checks
        if server is None:
            raise commands.CommandError("Command must be issued in a server")


        # Grab all songs from this server
        n, songs = await queue.grab_songs(server.id)

        # Check once more
        if len(songs) == 0:
            await ctx.send("🚫 This server has no queue currently. Start the party by queuing up a song!")
            return

        # Display songs
        await util.display_server_queue(ctx, songs, n)

    
    @commands.command(
            help="Skips the current song that is playing, can include number to skip more songs",
            aliases=['s'])
    async def skip(self, ctx: Context, n='1'):
        server = ctx.guild

        if server is None:
            raise commands.CommandError("Command must be issued in a server")

        if ctx.voice_client is None:
            raise commands.CommandError("I'm not in a voice channel")

        if not n.isdigit():
            raise commands.CommandError("Please enter a number to skip")
        n = int(n)

        if n <= 0:
            raise commands.CommandError("Please enter a positive number")

        # Skip specificed number of songs
        for _ in range(n-1):
            await queue.pop(server.id)

        # Safe to ignore error for now
        ctx.voice_client.stop()
