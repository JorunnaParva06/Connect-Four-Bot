import discord
from discord.ext import commands
import asyncio
import uuid

class Invite_Manager(commands.Cog):
    """
    Class contains commands and listeners for managing game invite instances
    Attributes:
        client: The bot client
        players: Dictionary containing invite instances
    """
    def __init__(self, client):
        """
        Initializes the cog with bot client
        Parameters: client of type commands.Bot
        Returns: None
        """
        self.client = client
        self.invites = {}
    
    @commands.Cog.listener()
    async def on_ready(self):
        """
        Prints a message when the file is running properly
        Parameters: self
        Returns: None
        """
        print("Success! invite_manager is active.")
    
    @ commands.Cog.listener()
    async def on_invite_resolved(self, invite_id):
        """
        Removes invites from the invites dictionary when no longer needed
        Parameters: self, unique invite ID of type UUID
        Returns: None
        """
        self.invites.pop(invite_id)
    
    @ commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """
        Calls for an invite instance to assign the yellow player when the proper reaction is added
        Parameters: self, reaction, user who reacted
        Returns: None
        """
        if reaction.emoji == "✅":
            for invite_id, invite in self.invites.items():
                if invite.message.id == reaction.message.id:
                    await invite.assign_yellow_player(user)
    
    @commands.command()
    async def play(self, ctx):
        """
        Sends an invite to initiate the game
        Parameters: self, ctx
        Returns: None
        """
        invite_id = uuid.uuid4()
        invite = Invite(self.client, invite_id, ctx)
        self.invites[invite_id] = invite
        await invite.setup_invite()  # Send invite message

class Invite():
    """
    Class contains functions related to inviting players to play connect four
    Attributes:
        client: The bot client
        players: Dict with keys containing player colors, values contain names and IDs
        channel: The channel where the invite was sent
        invite_id: Unique ID for the invite instance
        message: Display to be edited later
    """
    def __init__(self, client, invite_id, ctx):
        """
        Initializes the invite instance and sets up players
        Parameters: self, client of type commands.Bot, unique invite id of type UUID, ctx
        Returns: None
        """
        self.client = client
        self.players = {}
        self.channel = ctx.channel
        self.invite_id = invite_id
        self.players["red"] = [ctx.author.display_name, ctx.author.id]
        self.red_player_name = self.players["red"][0]
        self.message = None
    
    async def setup_invite(self):
        """
        Sends the initial invite message and checks for timeout
        Parameters: self
        Returns: None
        """
        embeded_msg = discord.Embed(title = f"{self.red_player_name} wants to play Connect Four!", description = "React using the green checkmark to play against them.", color = discord.Color.orange())
        self.message = await self.channel.send(embed = embeded_msg)
        await self.message.add_reaction("✅")
        await self.check_timeout()
    
    async def assign_yellow_player(self, user):
        """
        Assigns the yellow player and dispatches an event to start the game
        Parameters: self, user who reacted
        Returns: None
        """
        if not user.bot and self.players["red"][1] != user.id and "yellow" not in self.players:  # Ensure yellow player isn't a bot or the red player
            await self.message.delete()
            self.players["yellow"] = [user.display_name, user.id]
            self.dispatch_invite_resolved()
            game_id = uuid.uuid4()  # Generate a unique game ID
            self.client.dispatch("players_assigned", self.players, self.channel, game_id)  # Custom dispatch event called when both players assigned
    
    async def check_timeout(self):
        """
        Checks if the invite has timed out and dispatches an event if so
        Parameters: self
        Returns: None
        """
        await asyncio.sleep(60)  # Delete invite message after 60 seconds if nobody else reacts
        embeded_msg = discord.Embed(title = "Connect Four Game Cancelled", description = "Nobody else reacted after 60 seconds.", color = discord.Color.orange())
        await self.message.edit(embed = embeded_msg)
        self.dispatch_invite_resolved()
    
    def dispatch_invite_resolved(self):
        """
        Dispatches the invite resolved event, used for when an invite is cancelled or completed
        Parameters: self
        Returns: None
        """
        self.client.dispatch("invite_resolved", self.invite_id)

async def setup(client):
    await client.add_cog(Invite_Manager(client))
