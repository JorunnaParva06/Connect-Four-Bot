import discord
from discord.ext import commands
import asyncio
import uuid

class Invite_Game(commands.Cog):
    """
    Class contains commands and listeners related to sending game invites
    Attributes:
        client: The bot client
        players: Dictionary containing player info
        deleted_invite: Boolean to check if invite is deleted
    """
    def __init__(self, client):
        """
        Initializes the cog with bot client
        Parameters: client of type commands.Bot
        Returns: None
        """
        self.client = client
        self.players = {}
        self.deleted_invite = False
    
    @commands.Cog.listener()
    async def on_ready(self):
        """
        Prints a message when the file is running properly
        Parameters: self
        Returns: None
        """
        print("Success! invite_game is active.")
    
    @ commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """
        Assigns the yellow player based on whoever reacts with a checkmark first
        Parameters: self, reaction, user who reacted
        Returns: None
        """
        if "yellow" not in self.players:  # Only execute if no yellow player is assigned
            if reaction.emoji == "✅":  # If a different user reacts with checkmark emoji
                if not user.bot and self.players["red"][1] != user.id:
                    self.players["yellow"] = [user.display_name, user.id]
                    game_id = uuid.uuid4()  # Generate a unique game ID
                    self.client.dispatch("players_assigned", self.players, reaction.message.channel, game_id)  # Custom dispatch event called when both players assigned
                    self.deleted_invite = True
                    await self.message.delete()
                    self.players = {}  # Reset players after game starts

    @commands.command()
    async def play(self, ctx):
        """
        Sends an invite to initiate the game
        Parameters: self, ctx
        Returns: None
        """
        self.players["red"] = [ctx.author.display_name, ctx.author.id]
        embeded_msg = discord.Embed(title = f"{ctx.author.display_name} wants to play Connect Four!", description = "React using the green checkmark to play against them.", color = discord.Color.orange())
        self.message = await ctx.send(embed = embeded_msg)
        await self.message.add_reaction("✅")

        # Delete invite message after 60 seconds if nobody else reacts
        await asyncio.sleep(60)
        if not self.deleted_invite:  # Ensure invite embed is not already deleted
            self.deleted_invite = True
            await self.message.delete()
            await ctx.send("Connect Four game cancelled, nobody else reacted after 60 seconds.")

async def setup(client):
    await client.add_cog(Invite_Game(client))
