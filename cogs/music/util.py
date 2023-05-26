from discord.ext.commands.context import Context
from discord.ext.commands.converter import CommandError


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


# Check if command was entered in a server
async def in_server(ctx: Context):
    return ctx.guild != None 
