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

    def create_board(self):
        """
        Initializes the empty board at the start of the game
        Parameters: self
        Returns: 2D list representing empty board
        """
        num_rows = 6
        num_cols = 7
        board = []
        for i in range(num_rows):
            a_row = []
            for j in range(num_cols):
                a_row.append("⚪")
            board.append(a_row)
        return(board)
    
    def display_board(self, board):
        """
        Creates a string representation of the board
        Parameters: self, board of type 2D list
        Returns: String representing board
        """
        adjust_factor = 5
        display = ""
        for row in board:
            for element in row:
                display += element.rjust(adjust_factor)
            display += "\n"  # Create a new line
        return display
    
    @commands.command()
    async def sendembed(self, ctx):
        """
        Creates an embed with an image and example text
        Parameters: self, Context of the command
        Returns: None
        """
        board = self.create_board()
        embeded_msg = discord.Embed(title = "Title Example", description = "Description Example", color = discord.Color.red())
        embeded_msg.add_field(name="Field Name", value=self.display_board(board), inline=False)  # True will display fields on same line
        await ctx.send(embed = embeded_msg)

async def setup(client):
    await client.add_cog(Game_Functionality(client))
