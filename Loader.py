import numpy as np
import os

EMPTY = 1;
COLOR = 0;

BLACK = -1;
WHITE = 1;

WIDTH = 9;

def Flood(board, index, color): # Performs a flood fill to check if tiles are completely surrounded. If they are, then it returns a 1 and a list of the pieces to be captured.
    closed = [] # Closed List
    open_list = [index] # Open List

    x = index % WIDTH # X coordinate
    y = int(index / WIDTH) # Y coordinate
    if board[index, COLOR] != color:
        return -1, []
    while len(open_list) > 0:
        x = open_list[-1] % WIDTH
        y = int(open_list[-1] / WIDTH)
        closed.append(open_list.pop())

        for a in range(-1, 2): # This nested loop checks in the 4 cardinal directions adjacent to a tile
            for b in range(-1, 2):
                if (a == 0 or b == 0) and a != b: # <- make sure not to check diagonals
                    if a + y >= 0 and b + x >= 0 and a + y < WIDTH and b + x < WIDTH: # Make sure coords aren't out of bounds
                        idx = (x+b)+(y+a)*WIDTH # index, for simplification
                        if board[idx, EMPTY] == 1: # If it's empty, stop searching, there will be no capture here.
                            return -1, []
                        if board[idx, COLOR] == color: # If it's another allied stone, check to see if its liberties are taken
                            if not idx in closed and not idx in open_list: # Make sure that stone hasn't already been checked/will be checked to avoid infinite loops
                                open_list.append(idx)
    return 1, closed # No open tiles were ever found to stop the loop, so all liberties were taken.

def Move(bd, index, color): # Make a move. Return 1, board if successful, -1, parameter board if unsuccessful (ie suicide move)
    # Make a move at the index. color 1 = white, color -1 = black
    ENEMY = color * -1 # Opposite color of the player's
    board = np.array(bd) # This is done to make a shallow copy of the parameter

    board[index, COLOR] = color # This is where the move is made. 
    board[index, EMPTY] = 0

    # Check for captured pieces:
    x = index % WIDTH
    y = int(index / WIDTH)

    captured = []
    if x > 0: # Check for capture 1 sq to the left
        captured += Flood(board, (x-1)+y*WIDTH, ENEMY)[1]

    if x < WIDTH-1: # Check for capture 1 sq to the right
        captured += Flood(board, (x+1)+y*WIDTH, ENEMY)[1]

    if y > 0: # Check for capture 1 sq up
        captured += Flood(board, x+(y-1)*WIDTH, ENEMY)[1]

    if y < WIDTH-1: # Check for capture 1 sq down
        captured += Flood(board, x+(y+1)*WIDTH, ENEMY)[1]

    if len(captured) > 0:
        for i in captured:
            board[i, EMPTY] = 1
            board[i, COLOR] = 0
    
    if Flood(board, index, color)[0] != -1: # Check for Suicides
        return -1, bd
    
    return 1, board

def Decode_Move(move):
    if move == "":
        return 81
    else:
        xC = ord(move[0]) - ord('a')
        yC = ord(move[1]) - ord('a')
        if xC < 0 or xC > WIDTH or yC < 0 or yC > WIDTH:
            return -1
        return xC+yC*WIDTH

def createEmptyBoard():
    Board = np.zeros((82, 2))
    for x in range(len(Board)):
        Board[x, EMPTY] = 1
    Board[-1] = [-1, -1]
    return Board

def printBoard(board):
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
                #print(board[0])
                if board[x+y*WIDTH, COLOR] == BLACK:
                    string += ' @'
                elif board[x+y*WIDTH, COLOR] == WHITE:
                    string += ' O'
                elif board[x+y*WIDTH, EMPTY] == 1:
                    string += ' .'
        string += '\n'
    print(string)

Boards = []
Moves = []
def Main():
    path = ".\\go9"
    for entry in os.scandir(path): #I changed my mind i love python
        Go = True
        Board = createEmptyBoard() # 0 - 80 = [color, empty], 81 = [turn, turn]
        with open(entry) as f:
            if Go:
                for line in f:
                    if line[0] == ';': # this is the line with all the moves.
                        Go = False
                        copy = ""
                        for c in line:
                            if c != "[" and c != "]" and c != ")":
                                copy += c
                        arr = copy[1:].split(';')
                        for a in arr:
                            move = Decode_Move(a[1:])
                            if Decode_Move(a[1:]) == -1:
                                print(entry)
                                return
                            else:
                                color = 1
                                if(a[0] == 'B'):
                                    color = -1
                                Boards.append(Board)
                                Moves.append(Move)
                                if(move != 81):
                                    Board = Move(Board, move, color)[1]
Main()
Boards = np.array(Boards)
Moves = np.array(Moves)
print(len(Moves))
