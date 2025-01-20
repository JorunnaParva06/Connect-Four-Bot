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
        embeded_msg.add_field(name = "", value = self.display_board(self.board), inline = False)
        await self.message.edit(embed = embeded_msg)

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
    
    def find_adjacent(self, board, char, row_index, col_index):
        # Find the (row,col) coordinates of adjacent same colored pieces
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
        # determine the directions a win is possible in by subtracting each of the coords adjacent to the most recently placed by the most recently placed
        # x: the row portion of the (row,col) coords
        # y: the col portion of the (row,col) coords
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
    # based on a direction. Count the pieces in that direction to determine if the color wins. Return true if so
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
    
    @ commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """
        Changes board colors based on player input and switches turns
        Parameters: self, reaction object, user who reacted
        Returns: Int representing column number
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
            print(coords)
            
            directions = self.find_directions(coords, row_placed, column)
            print(directions)

            # Check win
            for direction in directions.keys():
                win = self.check_win(self.board, "Red" if self.red_turn else "Yellow", row_placed, column, direction)
                if win:
                    if self.red_turn:
                        winner = self.red_name
                        loser = self.yellow_name
                    else:
                        winner = self.yellow_name
                        loser = self.red_name
                    self.game_over = True

            # Check tie
            if self.check_tie(self.board):
                print("TIE")
                self.game_over = True

            # Check game over
            if self.game_over:
                self.client.dispatch("game_over", winner, loser)  # Custom dispatch event called when game ends
            
            self.red_turn = not self.red_turn
    
    @ commands.Cog.listener()
    async def on_game_over(self, winner, loser):
        """
        Updates the embed when the game ends
        Parameters: self, winner of type str, loser of type str
        Returns: None
        """
        embeded_msg = discord.Embed(title = "Game Over!", description = f"{winner} has beaten {loser} at Connect Four!", color = discord.Color.orange())
        embeded_msg.add_field(name = "", value = self.display_board(self.board), inline = False)
        await self.message.edit(embed = embeded_msg)

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
        self.red_name = self.players.get("red")[0]
        self.yellow_name = self.players.get("yellow")[0]
        self.red_id = self.players.get("red")[1]
        self.yellow_id = self.players.get("yellow")[1]
        self.game_over = False

        # Create initial embed, red will always go first
        embeded_msg = discord.Embed(title = "Red's Turn", description = f"{self.red_name} is Red, {self.yellow_name} is Yellow.", color = discord.Color.red())
        embeded_msg.add_field(name = "", value = self.display_board(self.board), inline = False)
        self.message = await channel.send(embed = embeded_msg)
        for move in moves:
            await self.message.add_reaction(move)
        
async def setup(client):
    await client.add_cog(Game_Functionality(client))
