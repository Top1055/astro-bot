from discord.ext import commands
from discord.ext.commands.context import Context

import cogs.music.util as util
import cogs.music.queue as queue
import cogs.music.translate as translate


from cogs.music.help import music_help

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


# Fix this pls

import json
#from .. import config
# Read data from JSON file in ./data/config.json
def read_data():
    with open("./data/config.json", "r") as file:
        return json.load(file)

    raise Exception("Could not load config data")


def get_spotify_creds():
    data = read_data()
    data = data.get("spotify")

    SCID = data.get("SCID")
    secret = data.get("SECRET")

    return SCID, secret






class music(commands.Cog):
    def __init__(self, client):
        self.client = client

        self.name = "🎶 Music"
        self.emoji = "🎶"

        help_command = music_help()
        help_command.cog = self
        self.help_command = help_command

        SCID, secret = get_spotify_creds()
        # Authentication - without user
        client_credentials_manager = SpotifyClientCredentials(client_id=SCID,
                                                      client_secret=secret)

        self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

        queue.initialize_tables()


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

        await util.join_vc(ctx)
        await ctx.message.add_reaction('👍')

        msg = await ctx.send("Fetching song(s)...")
        async with ctx.typing():
            #TODO potentially save requests before getting stream link
            # Grab video details such as title thumbnail duration
            audio = await translate.main(url, self.sp)

        await msg.delete()

        if len(audio) == 0:
            await ctx.message.add_reaction('🚫')
            await ctx.send("Failed to find song!")
            return


        #TODO make sure user isn't queuing in dm for some stupid reason

        # Setup first song's position
        audio[0]['position'] = await queue.add_song(
                server,
                audio[0],
                ctx.author.display_name)

        # Add any other songs
        for song in audio[1:]:
           await queue.add_song(
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
        if len(songs) == 0 and await queue.is_server_playing(ctx.guild.id) == False:
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
            await queue.pop(server.id, True)

        # Safe to ignore error for now
        ctx.voice_client.stop()