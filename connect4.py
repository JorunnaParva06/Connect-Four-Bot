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
    column = input('Enter column or \'exit\' to forfeit: ')
    if column == 'exit':
        return None
    while column not in ['0','1','2','3','4','5','6']:
        column = input('Invalid input. Enter column or \'exit\' to forfeit: ')
    return int(column)

def place_piece(board,color,row,column):
    board[row][column] = color.lower()[0]
    
def check_below(column, board):
    rows = len(board)
    for i in range(rows):
        if board[i][column] != '*':
            return i-1
    return rows-1

def find_adjacent(board,char, row_index, col_index):
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
    directions = {}
    for x,y in coords:
        if x-row_index == 0 and y-col_index in [-1,1]:
            directions['horizontal'] = True
        elif x-row_index in [-1,1] and y-col_index == 0:
            directions['verticle'] = True
        elif (x-row_index == -1 and y-col_index == -1) or (x-row_index == 1 and y-col_index == 1):
            directions['backslash-diag'] = True
        elif (x-row_index == 1 and y-col_index == -1) or (x-row_index == -1 and y-col_index == 1):
            directions['slash-diag'] = True
    return directions

def check_win(board,color,row_index,col_index,direction):
    rows = len(board)
    cols = len(board[0])
    count = 1
    char = color.lower()[0]

    if direction == 'horizontal':
        for i in range(1,4):
            if count == 4:
                break
            if col_index-i in range(cols):
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

        tie = check_tie(board)
        if tie:
            break
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
