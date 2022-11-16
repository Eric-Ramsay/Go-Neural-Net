import numpy as np
from IPython.display import clear_output # Used to clear previous prints for the ascii board
# Some Constants
WHITE = 0
BLACK = 1
EMPTY = 2
# Use to change board size
WIDTH = 9

def encode(board, color):
    space = 0
    out = str(color)
    for i in range(WIDTH*WIDTH):
        if board[i, EMPTY] == -1:
            if board[i, BLACK] == 1:
                out += "b"
            if board[i, WHITE] == 1:
                out += "w"
            if space > 0:
                out += "." + str(space) + "."
                space = 0
        else:
            space += 1
    return out

def decode(notation):
    index = 1
    strIndex = 0
    skip = 0
    board = np.zeros((WIDTH*WIDTH, 3))
    color = notation[0]
    board[:] = -1
    while index < WIDTH*WIDTH and strIndex < notation.size():
        if notation[strIndex] == 'b' or notation[strIndex] == 'w':
            board[index, EMPTY] = -1
            board[index, BLACK] = notation[strIndex] == 'b'
            board[index, WHITE] = not board[index, BLACK]
            index += 1
        elif notation[strIndex] == '.':
            skip = 0
            strIndex += 1
            while notation[strIndex] != '.':
                skip *= 10
                skip += notation[strIndex] - '0'
                strIndex += 1
            index += skip
    return board, color

def Flood(board, index, color):
    closed = [] # Closed List
    open = [index] # Open List
     # Board Size
    x = index % WIDTH # X coordinate
    y = int(index / WIDTH) # Y coordinate
    if board[index, color] == -1:
        return -1
    while len(open) > 0:
        x = open[-1] % WIDTH
        Y = int(open[-1] / WIDTH)
        closed.append(open.pop())
        if x > 0 and board[x-1+y*WIDTH, color] == 1:
            if not x-1+y*WIDTH in closed and not x-1+y*WIDTH in open:
                open.append(x-1+y*WIDTH)
        elif x > 0 and board[x-1+y*WIDTH, EMPTY] == 1:
            return -1, []
        if x < WIDTH-1 and board[x+1+y*WIDTH, color] == 1:
            if not x+1+y*WIDTH in closed and not x+1+y*WIDTH in open:
                open.append(x+1+y*WIDTH)
        elif x < WIDTH-1 and board[x+1+y*WIDTH, EMPTY] == 1:
            return -1, []
        if y > 0 and board[x+(y-1)*WIDTH, color] == 1:
            if not x+(y-1)*WIDTH in closed and not x+(y-1)*WIDTH in open:
                open.append(x+(y-1)*WIDTH)
        elif y > 0 and board[x+(y-1)*WIDTH, EMPTY] == 1:
            return -1, []
        if y < WIDTH-1 and board[x+(y+1)*WIDTH, color] == 1:
            if not x+(y+1)*WIDTH in closed and not x+(y+1)*WIDTH in open:
                open.append(x+(y+1)*WIDTH)
        elif y < WIDTH-1 and board[x+(y+1)*WIDTH, EMPTY] == 1:
            return -1, []
    return 1, closed

def Move(bd, index, color):
    # Make a move at the index. color 0 = white, color 1 = black
    ENEMY = abs(color-1)
    board = np.array(bd)
    board[index, EMPTY] = -1
    if color == 1:
        board[index, BLACK] = 1
        board[index, WHITE] = -1
    else:
        board[index, WHITE] = 1
        board[index, BLACK] = -1
    # Check for captured pieces:
    x = index % WIDTH
    y = int(index / WIDTH)
    captured = False
    if x > 0: # Check for capture 1 sq to the left
        capture = Flood(board, (x-1)+y*WIDTH, ENEMY)
        if capture != -1:
            captured = True
            for x in capture[1]:
                board[x, EMPTY] = 1
                board[x, WHITE] = -1
                board[x, BLACK] = -1
    if x < WIDTH-1: # Check for capture 1 sq to the right
        capture = Flood(board, (x+1)+y*WIDTH, ENEMY)
        if capture != -1:
            captured = True
            for x in capture[1]:
                board[x, EMPTY] = 1
                board[x, WHITE] = -1
                board[x, BLACK] = -1
    if y > 0: # Check for capture 1 sq up
        capture = Flood(board, x+(y-1)*WIDTH, ENEMY)
        if capture != -1:
            captured = True
            for x in capture[1]:
                board[x, EMPTY] = 1
                board[x, WHITE] = -1
                board[x, BLACK] = -1
    if y < WIDTH-1: # Check for capture 1 sq down
        capture = Flood(board, x+(y+1)*WIDTH, ENEMY)
        if capture != -1:
            captured = True
            for x in capture[1]:
                board[x, EMPTY] = 1
                board[x, WHITE] = -1
                board[x, BLACK] = -1
    if not captured: #Check for suicides
        capture = Flood(board, index, color)
        if capture[0] != -1:
            return -1, board
    return 1, board


def createMask(board, positions, color):
    mask = np.zeros(WIDTH*WIDTH)
    for a in range(WIDTH*WIDTH):
        mask[a] = board[a, EMPTY]
        current = ""
        for a in range(WIDTH*WIDTH):
            if mask[a]:
                variation = Move(board[:], a, color)
                if variation[0] == -1:
                    mask[a] = -1
                else:
                    if len(positions) > 0:
                        position = encode(variation[1], abs(color-1))
                        if position in positions:
                            mask[a] = -1
    return mask

def printBoard(board, turn):
    string = ""
    for y in range(-1, WIDTH):
        for x in range(-1, WIDTH):
            if x < 0:
                if y < 0:
                    string += '# '
                else:
                    string += str(y)+" "
            elif y < 0 and x > -1:
                string += ' ' + chr(65+x)
            else:
                if board[x+y*WIDTH, BLACK] == 1:
                    string += ' @'
                if board[x+y*WIDTH, WHITE] == 1:
                    string += ' O'
                if board[x+y*WIDTH, EMPTY] == 1:
                    string += ' .'
        string += '\n'
    print(string)

def main():
    board = np.zeros((WIDTH*WIDTH, 3))
    mask = np.zeros(WIDTH*WIDTH)
    positions = []
    board[:] = -1
    board[:, EMPTY] = 1
    color = 1
    val = ""
    xC = 0
    yC = 0
    while val != "quit":
        positions.append(encode(board, color))
        mask = createMask(board, positions, color)
        printBoard(board, 0)
        val = input("Enter your move: ")
        xC = ord(val[0]) - ord('a')
        if xC >= WIDTH or xC < 0:
            xC = ord(val[0]) - ord('A')
        yC = ord(val[1]) - ord('0')
        clear_output(wait=True)
        if mask[xC+yC*WIDTH] == 1:
            board = Move(board, xC+yC*WIDTH, color)[1]
            color = abs(color-1)
        else:
            print("Illegal move!", end = "\n")

main()