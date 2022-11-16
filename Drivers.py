
import numpy as np
import tensorflow.keras as keras
from keras.models import Model
from keras.layers import Dense, Input
import math

# Some Constants
WHITE = 1
BLACK = -1
EMPTY = 0
# Use to change board size
WIDTH = 9
BOARD_SIZE = WIDTH*WIDTH

def index_to_coordinate(index): #Returns row, column
    return int(index / WIDTH), index % WIDTH

def coordinate_to_index(x, y): #/Returns index
    return y*WIDTH+x

input_shape = (82, )

# The model needs to be created here. Right now this is a smaller convolutional network I made to try to reduce training times
model = keras.models.Sequential()
model.add(keras.layers.Dense(82, input_shape = input_shape, kernel_initializer='random_normal'))
model.add(keras.layers.Dense(82, activation = 'relu'))
model.add(keras.layers.Dense(82, activation = 'relu'))
model.add(keras.layers.Dense(82, activation = 'relu'))
model.add(keras.layers.Dense(82, activation = 'relu'))
model.add(keras.layers.Dense(82, activation = 'softmax'))


model.compile(loss=keras.losses.CategoricalCrossentropy(), optimizer = keras.optimizers.Adam(), metrics = [keras.metrics.CategoricalAccuracy()])

model.load_weights('mini_weights.h5')

def encode(board, color): # Converts a board position into a string, to reduce the memory needed to store past position states
    space = 0
    out = str(color)
    for i in range(WIDTH*WIDTH): # Loop through each tile on the board and encode it
        if board[i] != 0: # Non-Empty Tile
            if board[i] == BLACK: # Black piece
                out += "b"
            if board[i] == WHITE: # White piece
                out += "w"
            if space > 0: # Show that the previous streak of empty tiles has ended.
                out += "." + str(space) + "."
                space = 0
        else: # Space tells how many empty squares there were in a row before a piece was found. An empty board would be encoded as "" (best case), a full board as wbwbwbwb. . . (worst case)
            space += 1
    return out

def decode(notation): # Decodes a string created by the encode function and converts it to an array of length 81.
    index = 1
    strIndex = 0
    skip = 0
    board = np.zeros((WIDTH*WIDTH))
    color = notation[0]
    board[:] = -1
    while index < WIDTH*WIDTH and strIndex < notation.size():
        if notation[strIndex] == 'b' or notation[strIndex] == 'w':
            if notation[strIndex] == 'b': # Black Piece on this tile
                board[index] = BLACK
            else:                         # White piece on this tile
                board[index] = WHITE
            index += 1
        elif notation[strIndex] == '.':   # Empty tiles
            skip = 0
            strIndex += 1
            while notation[strIndex] != '.': # Streaks of empty tiles are coded as numbers followed by a period. This reads how many empty tiles there were, stopping once it sees a period.
                skip *= 10
                skip += notation[strIndex] - '0'
                strIndex += 1
            index += skip
    return board, color

def Flood(board, index, color): # Performs a flood fill to check if tiles are completely surrounded. If they are, then it returns a 1 and a list of the pieces to be captured.
    closed = [] # Closed List
    open = [index] # Open List

    x = index % WIDTH # X coordinate
    y = int(index / WIDTH) # Y coordinate
    if board[index] == color*-1:
        return []
    while len(open) > 0:
        x = open[-1] % WIDTH
        Y = int(open[-1] / WIDTH)
        closed.append(open.pop())
        if x > 0 and board[x-1+y*WIDTH] == color:
            if not x-1+y*WIDTH in closed and not x-1+y*WIDTH in open:
                open.append(x-1+y*WIDTH)
        elif x > 0 and board[x-1+y*WIDTH] == EMPTY:
            return -1, []
        if x < WIDTH-1 and board[x+1+y*WIDTH] == color:
            if not x+1+y*WIDTH in closed and not x+1+y*WIDTH in open:
                open.append(x+1+y*WIDTH)
        elif x < WIDTH-1 and board[x+1+y*WIDTH] == EMPTY:
            return -1, []
        if y > 0 and board[x+(y-1)*WIDTH] == color:
            if not x+(y-1)*WIDTH in closed and not x+(y-1)*WIDTH in open:
                open.append(x+(y-1)*WIDTH)
        elif y > 0 and board[x+(y-1)*WIDTH] == EMPTY:
            return -1, []
        if y < WIDTH-1 and board[x+(y+1)*WIDTH] == color:
            if not x+(y+1)*WIDTH in closed and not x+(y+1)*WIDTH in open:
                open.append(x+(y+1)*WIDTH)
        elif y < WIDTH-1 and board[x+(y+1)*WIDTH] == EMPTY:
            return -1, []
    return 1, closed

def Move(bd, index, color): # Make a move. Return 1, board if successful, -1, parameter board if unsuccessful (ie suicide move)
    # Make a move at the index. color 1 = white, color -1 = black
    ENEMY = color * -1 # Opposite color of the player's
    board = np.array(bd) # This is done to make a shallow copy of the parameter
    board[index] = color # This is where the move is made. 
    # Check for captured pieces:
    x = index % WIDTH
    y = int(index / WIDTH)
    captured = []
    if x > 0: # Check for capture 1 sq to the left
        captured += Flood(board, (x-1)+y*WIDTH, ENEMY)

    if x < WIDTH-1: # Check for capture 1 sq to the right
        captured += Flood(board, (x+1)+y*WIDTH, ENEMY)

    if y > 0: # Check for capture 1 sq up
        captured += Flood(board, x+(y-1)*WIDTH, ENEMY)

    if y < WIDTH-1: # Check for capture 1 sq down
        captured += Flood(board, x+(y+1)*WIDTH, ENEMY)

    if len(captured) > 0:
        for i in captured:
            board[i] = EMPTY
    else: #Check for suicides
        capture = Flood(board, index, color)
        if capture[0] != -1:
            return -1, bd

    return 1, board


def createMask(board, positions, color):
    mask = np.zeros(WIDTH*WIDTH)
    for a in range(WIDTH*WIDTH):
        mask[a] = 0
        if board[a] == EMPTY:
            mask[a] = 1
        current = ""
        for a in range(WIDTH*WIDTH):
            if mask[a]:
                variation = Move(board[:], a, color)
                if variation[0] == -1:
                    mask[a] = -1
                else:
                    if len(positions) > 0:
                        position = encode(variation[1], color*-1)
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
                    string += str(y+1)+" "
            elif y < 0 and x > -1:
                string += ' ' + chr(65+x)
            else:
                if board[x+y*WIDTH] == BLACK:
                    string += ' @'
                elif board[x+y*WIDTH] == WHITE:
                    string += ' O'
                elif board[x+y*WIDTH] == EMPTY:
                    string += ' .'
        string += '\n'
    print(string)

def stringToIndex(mv): 
    # Output 81 for pass,
    # 0-80 for a1-i8
    #-1 if invalid
    move = mv.lower()
    xC = 0
    yC = 0
    index = 0
    
    if move == "pass":
        return 81
    else:
        xC = ord(move[0]) - ord('a')
        yC = ord(move[1]) - ord('1')
        if xC < 0 or xC > WIDTH or yC < 0 or yC > WIDTH:
            return -1
        return xC+yC*WIDTH

def getEngineMove(bd, msk, color): # Get the index which the engine wants to move to.
    board = np.append(np.array([color]), bd)
    mask = np.append(np.array([0]), msk) # Size 82 np array, 0 = pass, 1-81 = board indexes
    net_moveList = (mask * model(np.array([board]), training=False)[0])
    net_move = 0
    for x in range(len(net_moveList)):
        if net_moveList[x] > net_moveList[net_move]:
            net_move = x
    return net_move-1

def main():
    board = np.zeros(WIDTH*WIDTH) # Board here is an 81 size array, but net has to have 82 size input
    positions = []
    color = -1
    
    val = ""
    xC = 0
    yC = 0
    
    while val != "quit":
        positions.append(encode(board, color))
        mask = createMask(board, positions, color)
        #clear_output(wait=True)
        printBoard(board, 0)
        string = "Enter "
        if False: # The net plays black's moves here.
            if color == BLACK:
                string = "Black's Move: "
            else: string = "White's Move: "
            net_move = getEngineMove(board, mask, color)
            if net_move > 0:
                board = Move(board, net_move, color)[1]
            color *= -1
            string += ": " + str(net_move) # Print what index the net choses to play at.
            print(string)
        else:
            string += "White's Move"
            val = input(string)
            if val == "pass":
                color *= -1
            elif val != "quit":
                val = stringToIndex(val)
                if val >= 0 and val < 81 and mask[val] == 1: # Check if the move is legal
                    board = Move(board, val, color)[1] # Make the move
                    color *= -1
                else:
                    print(mask[val])
                    #print("Illegal move!", end = "\n")
main()




