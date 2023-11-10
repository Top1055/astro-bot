# config.py
# This file should parse all configurations within the bot

import discord
from discord import Color
import json

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


# Reading prefix
def get_prefix():
    data = read_data()

    prefix = data.get('prefix')
    if prefix:
        return prefix

    raise Exception("Missing config data: prefix")


# Fetch the bot secret token
def get_login(bot):
    data = read_data()
    if data is False or data.get(f"{bot}bot") is False:
        raise Exception(f"Missing config data: {bot}bot")

    data = data.get(f"{bot}bot")
    return data.get("secret")


# Read the status and text data
def get_status():
    data = read_data()

    if data is False or data.get('status') is False:
        raise Exception("Missing config data: status")

    # Find type
    data = data.get('status')
    return translate_status(
            data.get('type'),
            data.get('text'),
            data.get('link')
            )

# Get colors from colorscheme
def get_color(color):
    data = read_data()

    if data is False or data.get('status') is False:
        raise Exception("Missing config data: color")

    # Grab color
    string_value = data.get("colorscheme").get(color)
    hex_value = Color.from_str(string_value)
    return hex_value


# Taking JSON variables and converting them into a presence
# Use None url incase not provided
def translate_status(status_type, status_text, status_url=None):
    if status_type == "playing":
        return discord.Activity(
                type=discord.ActivityType.playing,
                name=status_text
                )


    elif status_type == "streaming":
        return discord.Activity(
                type=discord.ActivityType.streaming,
                name=status_text,
                url=status_url
                )

    elif status_type == "listening":
        return discord.Activity(
                type=discord.ActivityType.listening,
                name=status_text
                )


    elif status_type == "watching":
        return discord.Activity(
                type=discord.ActivityType.watching,
                name=status_text
                )

    elif status_type == "competing":
        return discord.Activity(
                type=discord.ActivityType.competing,
                name=status_text
                )

    #TODO
    # Implement custom status type

    else:
        raise Exception(f"Invalid status type: {status_type}")
