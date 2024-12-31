import discord
from discord.ext import commands

class Game_Functionality(commands.Cog):
    """
    Class contains commands and listeners related to game functionality
    Attributes: client of type commands.Bot
    """
    def __init__(self, client):
        """
        Initializes the cog with bot client
        Parameters: client of type commands.Bot
        Returns: None
        """
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Prints a message when the bot is run
        Parameters: self
        Returns: None
        """
        print("Success! Bot is connected to Discord.")

    @commands.command()
    async def sendembed(self, ctx):
        """
        Creates an embed with an image and example text
        Parameters: self, Context of the command
        Returns: None
        """
        embeded_msg = discord.Embed(title = "Title Example", description = "Description Example", color = discord.Color.blue())
        embeded_msg.set_thumbnail(url = "https://m.media-amazon.com/images/I/81u7fuXcXQL.jpg")  # I found this on google images and pasted the link
        embeded_msg.add_field(name="Field Name", value="Field Value", inline=False)  # True will display fields on same line
        await ctx.send(embed = embeded_msg)

async def setup(client):
    await client.add_cog(Game_Functionality(client))