import discord
from discord.ext import commands

empty_space = "⚪"
red_space = "🔴"
yellow_space = "🟡"
moves = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣"]

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
        Prints a message when the file is running properly
        Parameters: self
        Returns: None
        """
        print("Success! game_functionality.py is active.")
    
    def create_board(self):
        """
        Initializes a 6 x 7 empty board at the start of the game
        Parameters: self
        Returns: 2D list representing empty board
        """
        # "*" signifies an empty space
        num_rows = 6
        num_cols = 7
        board = []
        for i in range(num_rows):
            a_row = []
            for j in range(num_cols):
                a_row.append("*")
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
                if element == "*":
                    element = empty_space
                elif element == "r":
                    element = red_space
                else:
                    element = yellow_space
                display += element.rjust(adjust_factor)
            display += "\n"  # Create a new line
        return display
    
    def update_board(self, board, column):
        """
        Updates the board based on player moves
        Parameters: self, board of type 2D list, column index of type int
        Returns: None
        """
        row_placed = self.check_below(self.board, column)
        if self.red_turn:
            board[row_placed][column] = "r"
        else:
            board[row_placed][column] = "y"
    
    def check_below(self, board, column):
        """
        Gets the lowest row a piece can be (i.e the highest index for an empty space character)
        Parameters: self, board of type 2D list, column index of type int
        Returns: highest possible row index of type int
        """
        rows = len(board)
        for i in range(rows):
            if board[i][column] != '*':
                return i - 1
        return rows - 1
    
    # Reaction listener
    @ commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """
        Changes board colors based on player input and switches turns
        Parameters: self, reaction object, user who reacted
        Returns: Int representing column number
        """
        # Red's move
        if self.red_turn and reaction.emoji in moves and user.id == self.players["red"][1]:  # Check if valid player reacted with valid emoji
            column = moves.index(reaction.emoji)
            self.update_board(self.board, column)
            
            # Update the embed
            embeded_msg = discord.Embed(title = "Title Example", description = "Yellow's Turn", color = discord.Color.yellow())
            embeded_msg.add_field(name= "", value = self.display_board(self.board), inline = False)
            await self.message.edit(embed = embeded_msg)

            self.red_turn = not self.red_turn
        # Yellow's move
        elif not self.red_turn and reaction.emoji in moves and user.id == self.players["yellow"][1]:  # Check if valid player reacted with valid emoji
            column = moves.index(reaction.emoji)
            self.update_board(self.board, column)
            
            # Update the embed
            embeded_msg = discord.Embed(title = "Title Example", description = "Red's Turn", color = discord.Color.red())
            embeded_msg.add_field(name= "", value = self.display_board(self.board), inline = False)
            await self.message.edit(embed = embeded_msg)

            self.red_turn = not self.red_turn

    @ commands.Cog.listener()
    async def on_players_assigned(self, players, channel):
        """
        Sets up initial game state when a red and yellow player is assigned
        Parameters: self, Context of the command
        Returns: None
        """
        self.board = self.create_board()
        self.players = players  # store players dictionary for reaction listener
        self.red_turn = True  # Red will always go first

        # Create initial embed, red will always go first
        embeded_msg = discord.Embed(title = "Title Example", description = "Red's Turn", color = discord.Color.red())
        embeded_msg.add_field(name = "", value = self.display_board(self.board), inline = False)
        self.message = await channel.send(embed = embeded_msg)
        for move in moves:
            await self.message.add_reaction(move)
        
        await self.start_game(channel, self.board, players)
        
async def setup(client):
    await client.add_cog(Game_Functionality(client))
