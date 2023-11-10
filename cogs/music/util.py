import discord
from discord.ext.commands.context import Context
from discord.ext.commands.converter import CommandError
import config
from . import queue

# Joining/moving to the user's vc in a guild
async def join_vc(ctx: Context):

    # Get the user's vc
    author_voice = getattr(ctx.author, "voice")
    if author_voice is None:
        # Raise exception if user is not in vc
        raise CommandError("User is not in voice channel")

    # Get user's vc
    vc = getattr(author_voice, "channel")
    if vc is None:
        raise CommandError("Unable to find voice channel")

    # Join or move to the user's vc
    if ctx.voice_client is None:
        await vc.connect()
    else:
        # Safe to ignore type error for now
        await ctx.voice_client.move_to(vc)


# Leaving the voice channel of a user
async def leave_vc(ctx: Context):
    # If the bot is not in a vc of this server
    if ctx.voice_client is None:
        raise CommandError("I am not in a voice channel")

    # if user is not in voice of the server
    author_voice = getattr(ctx.author, "voice")
    if author_voice is None:
        raise CommandError("You are not in a voice channel")

    # Make sure both bot and User are in same vc
    vc = ctx.voice_client.channel
    author_vc = getattr(author_voice, "channel")
    if author_vc is None or vc != author_vc:
        raise CommandError("You are not in this voice channel")

    # Disconnect
    await ctx.voice_client.disconnect(force=False)


# Build a display message for queuing a new song
async def queue_message(ctx: Context, data: dict):
    msg = discord.Embed(
            title=f"{ctx.author.display_name} queued a song!",
            color=config.get_color("main"))

    msg.set_thumbnail(url=data['thumbnail'])
    msg.add_field(name=data['title'],
                  value=f"Duration: {format_time(data['duration'])}" + '\n'
                  + f"Position: {data['position']}")

    await ctx.send(embed=msg)


# Build an embed message that shows the queue
async def display_server_queue(ctx: Context, songs, n):
    server = ctx.guild

    msg = discord.Embed(
            title=f"{server.name}'s Queue!",
            color=config.get_color("main"))

    display = f"🔊 Currently playing: ``{await queue.get_current_song(ctx.guild.id)}``\n\n"
    for i, song in enumerate(songs):
        display += f"``{i + 1}.`` {song[0]} - {format_time(song[1])} Queued by {song[2]}\n"
    msg.add_field(name="Songs:",
                  value=display,
                  inline=True)
    if n > 10:
        msg.set_footer(text=f"and {n - 10} more!..")

    await ctx.send(embed=msg)


# Converts seconds into more readable format
def format_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    elif minutes > 0:
        return f"{minutes}:{seconds:02d}"
    else:
        return f"{seconds} seconds"
