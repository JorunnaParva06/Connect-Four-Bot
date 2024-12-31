import discord
from discord.ext import commands
import os
import asyncio

client = commands.Bot(command_prefix = "=", intents = discord.Intents.all())

# Get token from external txt file
with open("important_codes.txt") as file:
    codes = file.readlines()
    token = codes[0]

async def load_cogs():
    """
    Loads cogs from cogs folder to extend functionality
    Parameters: None
    Returns: None
    """
    for filename in os.listdir("./cogs"):  # Search cogs folder for files
        if filename.endswith(".py"):  # Only load python files
            await client.load_extension(f"cogs.{filename[:-3]}")  # Remove '.py' and load as cog

async def main():
    async with client:
        await load_cogs()
        await client.start(token)

asyncio.run(main())