import discord
from discord.ext import commands
import asyncio

empty_space = "⚪"
red_space = "🔴"
yellow_space = "🟡"
moves = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣"]

class Game_Manager(commands.Cog):
    """
    Class contains commands and listeners for managing game instances
    Attributes:
        client: The bot client
        games: Dict to store game instances
    """
    def __init__(self, client):
        """
        Initializes the cog with bot client
        Parameters: client of type commands.Bot
        Returns: None
        """
        self.client = client
        self.games = {}

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Prints a message when the file is running properly
        Parameters: self
        Returns: None
        """
        print("Success! game_manager is active.")
    
    @ commands.Cog.listener()
    async def on_players_assigned(self, players, channel, game_id):
        """
        Creates a new game instance when players are assigned and stores it in a dictionary
        Parameters: self, players of type dict, text channel, unique game_id of type UUID
        Returns: None
        """
        game = Game(self.client, players, channel, game_id)
        self.games[game_id] = game
        await game.start_game()  # Start the game immediately

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """
        Listens for reactions on game messages and calls the move method of the corresponding game instance
        Parameters: self, reaction, user who reacted
        Returns: None
        """
        for game_id, game in self.games.items():
            if game.message.id == reaction.message.id:
                await game.move(reaction, user)
    
    @commands.Cog.listener()
    async def on_game_over(self, game_id):
        """
        Listens for if a game is over and removes it from dictionary
        Parameters: self, unique game id of type UUID
        Returns: None
        """
        self.games.pop(game_id)

class Game:
    """
    Class contains functions related to game functionality
    Attributes:
        client: The bot client
        board: 2D list representing the game board
        players: Dict with keys containing player colors, values contain names and IDs
        red_turn: Boolean indicating if it's red's turn
        game_over: Boolean indicating if the game is over
        channel: Text channel where the game is played
        game_id: Unique game ID
        message: Display to be edited later
        timeout_task: Background task for the timeout timer to prevent AFK
    """
    def __init__(self, client, players, channel, game_id):
        """
        Initializes the game and assigns players
        Parameters: client of type commands.Bot, players of type dict, text channel, unique game_id of type UUID
        Returns: None
        """
        self.client = client
        self.board = self.create_board()
        self.players = players
        self.red_turn = True  # Red will always go first
        self.game_over = False
        self.channel = channel
        self.game_id = game_id
        self.message = None
        self.timeout_task = None

        # Assign player names and IDs
        self.red_name = self.players.get("red")[0]
        self.yellow_name = self.players.get("yellow")[0]
        self.red_id = self.players.get("red")[1]
        self.yellow_id = self.players.get("yellow")[1]
    
    async def start_game(self):
        """
        Starts the game by sending the initial message and setting up the board
        Parameters: self
        Returns: None
        """
        # Create initial embed, red will always go first
        embeded_msg = discord.Embed(title = "Red's Turn", description = f"{self.red_name} is Red, {self.yellow_name} is Yellow.", color = discord.Color.red())
        embeded_msg.add_field(name = "", value = "You have 60 seconds to make your move.", inline = False)
        embeded_msg.add_field(name = "", value = self.display_board(self.board), inline = False)
        self.message = await self.channel.send(embed = embeded_msg)
        for move in moves:
            await self.message.add_reaction(move)
        await self.check_timeout("Red", discord.Color.red())  # Check if red player times out
    
    def create_board(self):
        """
        Initializes a 6 x 7 empty board at the start of the game
        Parameters: self
        Returns: 2D list representing empty board
        """
        num_rows = 6
        num_cols = 7
        board = []
        for i in range(num_rows):
            a_row = []
            for j in range(num_cols):
                a_row.append("*")  # "*" signifies an empty space
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

    def update_board(self, row_placed, board, column):
        """
        Updates the board based on player moves
        Parameters: self, board of type 2D list, column index of type int
        Returns: None
        """
        if self.red_turn:
            board[row_placed][column] = "r"
        else:
            board[row_placed][column] = "y"
    
    async def update_embed(self):
        """
        Updates the embed showing the game board and who's turn it is
        Parameters: self
        Returns: None
        """
        if self.red_turn:
            next_player = "Yellow"
            color = discord.Color.yellow()
        else:
            next_player = "Red"
            color = discord.Color.red()
        embeded_msg = discord.Embed(title = f"{next_player}'s Turn", description = f"{self.red_name} is Red, {self.yellow_name} is Yellow.", color = color)
        embeded_msg.add_field(name = "", value = "You have 60 seconds to make your move.", inline = False)
        embeded_msg.add_field(name = "", value = self.display_board(self.board), inline = False)
        await self.message.edit(embed = embeded_msg)

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
    
    def find_adjacent(self, board, char, row_index, col_index):
        """
        Finds the coordinates of adjacent same colored pieces
        Parameters: self, board of type 2D list, char of type str, row index of type int, column index of type int
        Returns: List of tuples containing coordinates of adjacent pieces
        """
        rows = len(board)
        cols = len(board[0])
        coords = []
        # Up
        if row_index-1 in range(rows):
            if board[row_index-1][col_index] == char:
                coords.append((row_index-1,col_index))
        # Down
        if row_index+1 in range(rows):
            if board[row_index+1][col_index] == char:
                coords.append((row_index+1,col_index))
        # Left
        if col_index-1 in range(cols):
            if board[row_index][col_index-1] == char:
                coords.append((row_index,col_index-1))
        # Right
        if col_index+1 in range(cols):
            if board[row_index][col_index+1] == char:
                coords.append((row_index,col_index+1))
        # Up-Left
        if row_index-1 in range(rows) and col_index-1 in range(cols):
            if board[row_index-1][col_index-1] == char:
                coords.append((row_index-1,col_index-1))
        # Up-Right
        if row_index-1 in range(rows) and col_index+1 in range(cols):
            if board[row_index-1][col_index+1] == char:
                coords.append((row_index-1,col_index+1))
        # Down-Left
        if row_index+1 in range(rows) and col_index-1 in range(cols):
            if board[row_index+1][col_index-1] == char:
                coords.append((row_index+1,col_index-1))
        # Down-Right
        if row_index+1 in range(rows) and col_index+1 in range(cols):
            if board[row_index+1][col_index+1] == char:
                coords.append((row_index+1,col_index+1))

        return coords
    
    def find_directions(self, coords, row_index, col_index):
        """
        Determines the directions a win is possible in
        Parameters: self, coords of type list of tuples, row index of type int, column index of type int
        Returns: Dictionary of directions with boolean values
        """
        # row_index: row index of the most recently placed piece
        # col_index: col index of the most recently placed piece

        directions = {}
        # dictionary to ignore repeats

        for x,y in coords:
            # Horizontal wins -> there's only a difference of index in the columns
            if x-row_index == 0 and y-col_index in [-1,1]:
                directions['horizontal'] = True
            # Verticle wins -> there's only a difference of index in the rows
            elif x-row_index in [-1,1] and y-col_index == 0:
                directions['verticle'] = True
            # backslash diagonal wins -> there must either be a exclusively positive or negative difference of index in the rows and columns
            elif (x-row_index == -1 and y-col_index == -1) or (x-row_index == 1 and y-col_index == 1):
                directions['backslash-diag'] = True
            # slash diagonal wins -> you get the idea
            elif (x-row_index == 1 and y-col_index == -1) or (x-row_index == -1 and y-col_index == 1):
                directions['slash-diag'] = True
        return directions
    
    def check_win(self, board, color, row_index, col_index, direction):
        """
        Checks if a player has won by counting the pieces in a given direction
        Parameters: self, board of type 2D list, color of type str, row index of type int, column index of type int, direction of type str
        Returns: Count of linked of pieces of type int
        """
        rows = len(board)
        cols = len(board[0])
        count = 1
        char = color.lower()[0]

        # based on the recent placement, count adjacent pieces moving outward (think like a water drop on undistrubed water)
        if direction == 'horizontal':
            # Range (1,4) so we start counting the spaces +-1 through +-3
            for i in range(1,4):
                # Once we connect 4, stop checking. Applies for each of these conditionals
                if count == 4:
                    break
                # Double "if" statements to prevent accessing a nonexistent index. Applies for each of these conditionals
                if col_index-i in range(cols):
                    # check if the board at the index is the same color piece and the previous one in this direction was a same color piece
                    if board[row_index][col_index-i] == char and board[row_index][col_index-i+1] == char:
                        count+=1
                if col_index+i in range(cols):
                    if board[row_index][col_index+i] == char and board[row_index][col_index+i-1] == char:
                        count+=1
        elif direction == 'verticle':
            for i in range(1,4):
                if count == 4:
                    break
                if row_index-i in range(rows):
                    if board[row_index-i][col_index] == char and board[row_index-i+1][col_index] == char:
                        count+=1
                if row_index+i in range(rows):
                    if board[row_index+i][col_index] == char and board[row_index+i-1][col_index] == char:
                        count+=1
        elif direction == 'backslash-diag':
            for i in range(1,4):
                if count == 4:
                    break
                if row_index-i in range(rows) and col_index-i in range(cols):
                    if board[row_index-i][col_index-i] == char and board[row_index-i+1][col_index-i+1] == char:
                        count+=1
                if row_index+i in range(rows) and col_index+i in range(cols):
                    if board[row_index+i][col_index+i] == char and board[row_index+i-1][col_index+i-1] == char:
                        count+=1
        elif direction == 'slash-diag':
            for i in range(1,4):
                if count == 4:
                    break
                if row_index+i in range(rows) and col_index-i in range(cols):
                    if board[row_index+i][col_index-i] == char and board[row_index+i-1][col_index-i+1] == char:
                        count+=1
                if row_index-i in range(rows) and col_index+i in range(cols):
                    if board[row_index-i][col_index+i] == char and board[row_index-i+1][col_index+i-1] == char:
                        count+=1
        return count == 4
    
    def check_tie(self, board):
        """
        Counts each piece on the board and determines if it is full 
        Parameters: self, board of type 2D list
        Returns: True or False based on if board is full
        """
        full_count = 0
        num_rows = len(board)
        num_cols = len(board[0])
        for i in range(num_rows):
            for j in range(num_cols):
                if board[i][j] != '*':
                    full_count += 1
        return full_count == num_rows * num_cols
    
    async def game_won(self, winner, loser, color):
        """
        Updates the embed when a player wins
        Parameters: self, winner of type str, loser of type str
        Returns: None
        """
        embeded_msg = discord.Embed(title = "Game Over!", description = f"{winner} has beaten {loser} at Connect Four!", color = color)
        embeded_msg.add_field(name = "", value = self.display_board(self.board), inline = False)
        await self.message.edit(embed = embeded_msg)
        self.dispatch_game_over()
    
    async def game_tied(self):
        """
        Updates the embed when the game ties
        Parameters: self
        Returns: None
        """
        embeded_msg = discord.Embed(title = "Game Over!", description = f"The game is a tie, neither {self.red_name} or {self.yellow_name} won.", color = discord.Color.orange())
        embeded_msg.add_field(name = "", value = self.display_board(self.board), inline = False)
        await self.message.edit(embed = embeded_msg)
        self.dispatch_game_over()
    
    async def timeout_timer(self, player, color):
        """
        Counts down time for a move and cancels game if timeout occurs, does nothing otherwise
        Parameters: self, player color of type str, color of type discord.Color
        Returns: None
        """
        try:
            await asyncio.sleep(60)
            self.game_over = True
            embeded_msg = discord.Embed(title = "Connect Four game cancelled", description = f"{player} has timed out.", color = color)
            embeded_msg.add_field(name = "", value = self.display_board(self.board), inline = False)
            await self.message.edit(embed = embeded_msg)
            self.dispatch_game_over()
        except asyncio.CancelledError:
            pass  # If task is cancelled, do nothing
    
    def check_timeout(self, player, color):
        """
        Checks if a player times out by creating coroutines to act as a turn timer
        Parameters: self, player color of type str, color of type discord.Color
        Returns: None
        """
        if self.timeout_task:
            self.timeout_task.cancel()  # Cancel previous task
        self.timeout_task = asyncio.create_task(self.timeout_timer(player, color))  # Create new task if there is no previous task    
    
    def dispatch_game_over(self):
        """
        Dispatches a custom event when the game is over
        Parameters: self
        Returns: None
        """
        self.client.dispatch("game_over", self.game_id)

    async def move(self, reaction, user):
        """
        Processes a player's move, checking victory conditions, updating the board and timeouts
        Parameters: self, reaction, user who reacted
        Returns: None
        """
        if not self.game_over:

            # Red's move
            if self.red_turn and reaction.emoji in moves and user.id == self.red_id:  # Check if valid player reacted with valid emoji
                column = moves.index(reaction.emoji)
                row_placed = self.check_below(self.board, column)
                while row_placed < 0:  # While the chosen column is full
                    reaction = await self.client.wait_for('reaction_add', check = lambda u, r : u == user and r.emoji in moves)  # Get another reaction until valid

            # Repeat for Yellow's move
            elif not self.red_turn and reaction.emoji in moves and user.id == self.yellow_id:
                column = moves.index(reaction.emoji)
                row_placed = self.check_below(self.board, column)
                while row_placed < 0:
                    reaction = await self.client.wait_for('reaction_add', check = lambda u, r : u == user and r.emoji in moves)
            
            self.update_board(row_placed, self.board, column)   
            await self.update_embed()
            
            coords = self.find_adjacent(self.board, "r" if self.red_turn else "y", row_placed, column)
            
            directions = self.find_directions(coords, row_placed, column)

            # Check win
            for direction in directions.keys():
                win = self.check_win(self.board, "Red" if self.red_turn else "Yellow", row_placed, column, direction)
                if win:
                    if self.red_turn:
                        winner = self.red_name
                        loser = self.yellow_name
                        color = discord.Color.red()
                    else:
                        winner = self.yellow_name
                        loser = self.red_name
                        color = discord.Color.yellow()
                    self.game_over = True
                    await self.game_won(winner, loser, color)

            # Check tie
            if self.check_tie(self.board):
                self.game_over = True
                await self.game_tied()
            
            self.red_turn = not self.red_turn  # Switch turns

            self.check_timeout("Red" if self.red_turn else "Yellow", discord.Color.red() if self.red_turn else discord.Color.yellow())
        
async def setup(client):
    await client.add_cog(Game_Manager(client))
