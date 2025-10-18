import datetime
import discord

def success(content: str):
    embed = discord.Embed(
        description=f"### :jack_o_lantern: {content}",
        color=discord.Color.orange()
    )
    
    embed.timestamp = datetime.datetime.now(datetime.timezone.utc)
    
    return embed

def error(content: str):
    embed = discord.Embed(
        description=f":x: {content}",
        color=discord.Color.red()
    )
    
    embed.timestamp = datetime.datetime.now(datetime.timezone.utc)
    
    return embed