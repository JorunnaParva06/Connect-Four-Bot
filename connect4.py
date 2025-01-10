border = '🟦'
empty = '⚪'
red = '🔴'
yellow = '🟡'
def create_board() -> list:
    # Make a 6 x 7 board
    # * signifies an empty space
    rows = 6
    cols = 7
    board = []
    for i in range(rows):
        row = []
        for j in range(cols):
            row.append('*')
        board.append(row)
    return board

def display_board(board): 
    # Display emojis depending on the character of {board} plus a surrounding border
    margin = 1
    print(border*(len(board[0]) + margin*2))
    
    for i in range(len(board)):
        print(border,end='')
        for j in range(len(board[0])):
            if board[i][j] == '*':
                print(f'{empty}', end='')
            elif board[i][j] == 'r':
                print(f'{red}',end='')
            else:
                print(f'{yellow}',end='') 
        print(border)

    print(border,end='')
    for i in range (len(board[0])):
        print(f' {i}',end='')
    print(border)

def get_column():
    # Gets user input
    column = input('Enter column or \'exit\' to forfeit: ')
    while column not in ['0','1','2','3','4','5','6','exit']:
        column = input('Invalid input. Enter column or \'exit\' to forfeit: ')
    if column == 'exit':
        return None
    return int(column)

def place_piece(board,color,row,column):
    # Places a piece
    board[row][column] = color.lower()[0]
    
def check_below(column, board):
    # find and return the "lowest" row a piece can be (i.e the highest index for an empty space character)
    rows = len(board)
    for i in range(rows):
        if board[i][column] != '*':
            return i-1
    return rows-1

def find_adjacent(board,char, row_index, col_index):
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

def find_directions(coords,row_index,col_index):
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

def check_win(board,color,row_index,col_index,direction):
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

def check_tie(board):
    # count the board to see if full
    full_count = 0
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] != '*':
                full_count+=1
    return full_count == 42

def main():
    print('WELCOME TO CONNECT 4')
    board = create_board()
    display_board(board)
    tie = False
    win = False
    forfeit = False
    while not win or not tie or forfeit:
        print('Red Turn')

        column = get_column()
        if column == None:
            forfeit = True
            break

        row = check_below(column,board)
        while row == -1:
            print('Column full.')
            column = get_column()
            row = check_below(column,board)

        place_piece(board,'red',row,column)
        display_board(board)
        coords = find_adjacent(board,'r',row,column)
        directions = find_directions(coords,row,column)
        print(directions)
        for direction in directions.keys():
            win = check_win(board, 'Red', row, column, direction)
            if win:
                winner = 'Red'
                break
        # escape the while loop once we encounter a tie or win
        if win:
            break
        tie = check_tie(board)
        if tie:
            break

        print('Yellow Turn')
        column = get_column()
        if column == None:
            forfeit = True
            break
        row = check_below(column,board)
        while row == -1:
            print('Column full.')
            column = get_column()
            row = check_below(column,board)
        place_piece(board,'yellow',row,column)
        display_board(board)
        coords = find_adjacent(board,'y',row,column)
        directions = find_directions(coords,row,column)
        print(directions)
        for direction in directions.keys():
            win = check_win(board, 'Yellow', row, column, direction)
            if win:
                winner = 'Yellow'
                break
        
        # escape the while loop once we encounter a tie or win
        if win:
            break
        tie = check_tie(board)
        if tie:
            break

    # show the results
    if forfeit:
        print('Game forfeited.')
    elif not tie:
        print('#'*9)
        print(f'{winner} Wins!')
        print('#'*9)
    elif tie:
        print('It\'s a tie!')


if __name__ == '__main__':
    main()
