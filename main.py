import asyncio
import logging
import os
import traceback
import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()


TOKEN = os.getenv("TOKEN")    
intents = discord.Intents.all()
prefix = "r!"

client = commands.Bot(command_prefix=prefix, intents=intents)

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game("Ghosts 👻"), status=discord.Status.dnd)
    print("logged in!!")
    
@client.command()
@commands.is_owner()
async def update(ctx:commands.Context):
    try:
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py") and not filename.endswith("rbchat.py"):
                await client.reload_extension(f"cogs.{filename[:-3]}")
        await ctx.send(embed=discord.Embed(
            title=":white_check_mark: Succesfully updated the bot!",
            description="Updates applied from all the cogs!",
            color=discord.Color.green()
        ))
    except:
        logging.error(f"ERROR FOUND!: {traceback.format_exc()}")
        await ctx.send(embed=discord.Embed(
            title=":x: Fatal Error!",
            description=":scream: Could not reload cogs, Check your terminal for more information.",
            color=discord.Color.red()
        ))
    
async def load():
    for filename in os.listdir("cogs"):
        if filename.endswith(".py"):
            await client.load_extension(f"cogs.{filename[:-3]}")
            
async def main():
    async with client:
        await load()
        await client.start(TOKEN)
        
asyncio.run(main())