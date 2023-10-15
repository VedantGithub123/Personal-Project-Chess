# Title: ISC3UO Final Project - Chess
# Developer: Vedant Nehete
# Purpose: The purpose of this project is to create a chess software where a player can
#     play against another player or an engine created using ML models and/or algorithms
# Version: 1.0
# Version History:
#    1.0 : Structure of chess game
# Needs: Finish getPossibleMoves()

# Import libraries here
import numpy as np
import pygame as pg
import copy
import time
import random


# Defines functions below
def boardFromNums(nums):  # Creates a board from a list of strings
  # Converts the list into a list of ints and reshapes it into a 3D np array
  return np.array(list(map(int, nums))).reshape((8, 8, 2))

def deepTuple(board): # Creates a deep copy with tuples instead of lists
  # Iterates 3 times for each layer of the array to convert it into tuples
  return tuple(tuple(tuple(j) for j in i) for i in board)

def fileAddData(board, eval):  # Writes the board to a file in a certain format
  # Flattens the board and joins it with a " " between the different values
  if deepTuple(board) not in boardToEvalAlgo:
    dataFileAlgo.write(" ".join(map(str, board.flatten())) + " " + str(eval) + "\n")

def makeMove(move):  # Changes the chessboard and swaps the turn
  # Says we are changing the global vairables instead of new ones in a smaller scope
  global chessBoard
  global turn
  global prevBoard
  turn = 3 - turn
  boardAsTuple = deepTuple(chessBoard)
  if boardAsTuple in prevMoves:
    prevMoves[boardAsTuple] += 1
  else:
    prevMoves[boardAsTuple] = 1
  prevBoard = copy.deepcopy(chessBoard)
  chessBoard = copy.deepcopy(move)
  
def evaluatePos(board):  # Uses points to evaulate the position of the board
  # Adds together the different point values, subtracts if black's pieces
  sum = 0
  for x, i in enumerate(board):
    for y, j in enumerate(i):
      val = lambda x: x
      if j[1] == BLACK:
        val = lambda x: -1*x
      if j[0] == PAWN:
        if j[1] == BLACK:
          sum+=val(VALUES[j[0]])*(1.035-abs(x-3.5)/50)*(1.035-abs(y-3.5)/50)*(0.005*x+0.9625)
        else:
          sum+=val(VALUES[j[0]])*(1.035-abs(x-3.5)/50)*(1.035-abs(y-3.5)/50)*(0.005*(7-x)+0.9625)
      elif j[0] != KING:
        sum+=val(VALUES[j[0]])*(1.035-abs(x-3.5)/50)*(1.035-abs(y-3.5)/50)
  return sum * (2-(pointSum(board)-VALUES[KING]*2)/50)

def pointSum(board):  # Gets the total number of points on the board
  # Adds together the different point values
  sum = 0
  for i in board:
    for j in i:
      sum += VALUES[j[0]]
  return sum

def inCheck(board, t):  # Function to check if the king in in check
  # Finds the position of the king on the board
  for y in range(8):
    for x in range(8):
      if board[x][y][1] == t and board[x][y][0] == KING:
        # After finding the king, it checks if there are any pieces pointing at it
        # Checks if a rook is attacking the king
        tempX = x + 1
        tempY = y
        while tempX >= 0 and tempX < 8:
          if board[tempX][tempY][1] == t or (board[tempX][tempY][1] == 3-t and board[tempX][tempY][0] != ROOK):
            break
          if board[tempX][tempY][0] == ROOK:
            return True
          tempX += 1
        tempX = x - 1
        while tempX >= 0 and tempX < 8:
          if board[tempX][tempY][1] == t or (board[tempX][tempY][1] == 3-t and board[tempX][tempY][0] != ROOK):
            break
          if board[tempX][tempY][0] == ROOK:
            return True
          tempX -= 1
        tempX = x
        tempY = y+1
        while tempY >= 0 and tempY < 8:
          if board[tempX][tempY][1] == t or (board[tempX][tempY][1] == 3-t and board[tempX][tempY][0] != ROOK):
            break
          if board[tempX][tempY][0] == ROOK:
            return True
          tempY += 1
        tempY = y - 1
        while tempY >= 0 and tempY < 8:
          if board[tempX][tempY][1] == t or (board[tempX][tempY][1] == 3-t and board[tempX][tempY][0] != ROOK):
            break
          if board[tempX][tempY][0] == ROOK:
            return True
          tempY -= 1
        
        # Checks if a bishop is attacking the king
        tempX = x + 1
        tempY = y + 1
        while tempX >= 0 and tempX < 8 and tempY >= 0 and tempY < 8:
          if board[tempX][tempY][1] == t or (board[tempX][tempY][1] == 3-t and board[tempX][tempY][0] != BISHOP):
            break
          if board[tempX][tempY][0] == BISHOP:
            return True
          tempX += 1
          tempY += 1
        tempX = x - 1
        tempY = y - 1
        while tempX >= 0 and tempX < 8 and tempY >= 0 and tempY < 8:
          if board[tempX][tempY][1] == t or (board[tempX][tempY][1] == 3-t and board[tempX][tempY][0] != BISHOP):
            break
          if board[tempX][tempY][0] == BISHOP:
            return True
          tempX -= 1
          tempY -= 1
        tempX = x + 1
        tempY = y - 1
        while tempX >= 0 and tempX < 8 and tempY >= 0 and tempY < 8:
          if board[tempX][tempY][1] == t or (board[tempX][tempY][1] == 3-t and board[tempX][tempY][0] != BISHOP):
            break
          if board[tempX][tempY][0] == BISHOP:
            return True
          tempX += 1
          tempY -= 1
        tempX = x - 1
        tempY = y + 1
        while tempX >= 0 and tempX < 8 and tempY >= 0 and tempY < 8:
          if board[tempX][tempY][1] == t or (board[tempX][tempY][1] == 3-t and board[tempX][tempY][0] != BISHOP):
            break
          if board[tempX][tempY][0] == BISHOP:
            return True
          tempX -= 1
          tempY += 1
        
        # Checks if a queen is attacking the king
        tempX = x + 1
        tempY = y
        while tempX >= 0 and tempX < 8:
          if board[tempX][tempY][1] == t or (board[tempX][tempY][1] == 3-t and board[tempX][tempY][0] != QUEEN):
            break
          if board[tempX][tempY][0] == QUEEN:
            return True
          tempX += 1
        tempX = x - 1
        while tempX >= 0 and tempX < 8:
          if board[tempX][tempY][1] == t or (board[tempX][tempY][1] == 3-t and board[tempX][tempY][0] != QUEEN):
            break
          if board[tempX][tempY][0] == QUEEN:
            return True
          tempX -= 1
        tempX = x
        tempY = y+1
        while tempY >= 0 and tempY < 8:
          if board[tempX][tempY][1] == t or (board[tempX][tempY][1] == 3-t and board[tempX][tempY][0] != QUEEN):
            break
          if board[tempX][tempY][0] == QUEEN:
            return True
          tempY += 1
        tempY = y - 1
        while tempY >= 0 and tempY < 8:
          if board[tempX][tempY][1] == t or (board[tempX][tempY][1] == 3-t and board[tempX][tempY][0] != QUEEN):
            break
          if board[tempX][tempY][0] == QUEEN:
            return True
          tempY -= 1
        tempX = x + 1
        tempY = y + 1
        while tempX >= 0 and tempX < 8 and tempY >= 0 and tempY < 8:
          if board[tempX][tempY][1] == t or (board[tempX][tempY][1] == 3-t and board[tempX][tempY][0] != QUEEN):
            break
          if board[tempX][tempY][0] == QUEEN:
            return True
          tempX += 1
          tempY += 1
        tempX = x - 1
        tempY = y - 1
        while tempX >= 0 and tempX < 8 and tempY >= 0 and tempY < 8:
          if board[tempX][tempY][1] == t or (board[tempX][tempY][1] == 3-t and board[tempX][tempY][0] != QUEEN):
            break
          if board[tempX][tempY][0] == QUEEN:
            return True
          tempX -= 1
          tempY -= 1
        tempX = x + 1
        tempY = y - 1
        while tempX >= 0 and tempX < 8 and tempY >= 0 and tempY < 8:
          if board[tempX][tempY][1] == t or (board[tempX][tempY][1] == 3-t and board[tempX][tempY][0] != QUEEN):
            break
          if board[tempX][tempY][0] == QUEEN:
            return True
          tempX += 1
          tempY -= 1
        tempX = x - 1
        tempY = y + 1
        while tempX >= 0 and tempX < 8 and tempY >= 0 and tempY < 8:
          if board[tempX][tempY][1] == t or (board[tempX][tempY][1] == 3-t and board[tempX][tempY][0] != QUEEN):
            break
          if board[tempX][tempY][0] == QUEEN:
            return True
          tempX -= 1
          tempY += 1
        
        # Checks if a knight is attacking the king
        knightMoves = [[1, 2], [1, -2], [-1, 2], [-1, -2], [2, 1], [2, -1],
                         [-2, 1], [-2, -1]]
        for i in knightMoves:
          if x+i[0]>=0 and x+i[0]<8 and y+i[1]>=0 and y+i[1]<8:
            if board[x+i[0]][y+i[1]][1]==3-t and board[x+i[0]][y+i[1]][0] == KNIGHT:
              return True

        # Checks if a pawn is attacking the king
        tempX = x
        tempY = y
        if t==BLACK:
          try:
            if board[tempX+1][tempY+1][0] == PAWN and board[tempX+1][tempY+1][1] == WHITE:
              return True
          except:
            pass
          try:
            if board[tempX+1][tempY-1][0] == PAWN and board[tempX+1][tempY-1][1] == WHITE and tempY != 0:
              return True
          except:
            pass
        else:
          try:
            if board[tempX-1][tempY+1][0] == PAWN and board[tempX-1][tempY+1][1] == BLACK:
              return True
          except:
            pass
          try:
            if board[tempX-1][tempY-1][0] == PAWN and board[tempX-1][tempY-1][1] == BLACK and tempY != 0:
              return True
          except:
            pass

        # Checks if a king is attacking the king (Should never happen but is here due to the way the code works)
        tempX = x
        tempY = y
        try:
          if board[tempX+1][tempY][0] == KING:
            return True
        except:
          pass
        try:
          if board[tempX+1][tempY-1][0] == KING and tempY != 0:
            return True
        except:
          pass
        try:
          if board[tempX][tempY-1][0] == KING and tempY != 0:
            return True
        except:
          pass
        try:
          if board[tempX-1][tempY-1][0] == KING and tempY != 0 and tempX != 0:
            return True
        except:
          pass
        try:
          if board[tempX-1][tempY][0] == KING and tempX != 0:
            return True
        except:
          pass
        try:
          if board[tempX-1][tempY+1][0] == KING and tempX != 0:
            return True
        except:
          pass
        try:
          if board[tempX][tempY+1][0] == KING:
            return True
        except:
          pass
        try:
          if board[tempX+1][tempY+1][0] == KING:
            return True
        except:
          pass

        # If there is nothing pointing at the king, returns False
        return False

def isCheckmate(board, t):
  # If the king is in check and there are no moves, return True, else False
  return inCheck(board, t) and len(getPossibleMoves(board, t)) == 0

def isStalemate(board, t):
  # Checks if the king is not in check and there are no moves
  # Or if the same situation arose 3 times
  # Or there are only 2 kings
  # Or only 2 kings and a minor piece
  return ((not inCheck(board, t) and len(getPossibleMoves(board, t)) == 0)
          or any(i >= 3 for i in prevMoves.values())
          or pointSum(board) == VALUES[KING] + VALUES[KING]
          or (pointSum(board) == VALUES[KING] + VALUES[KING] + VALUES[KNIGHT] and all(i[0]!=PAWN for i in board)) # Same as KING+KING+BISHOP
          )

def getPossibleMoves(board, t):
  newBoards = []
  for y in range(8):
    for x in range(8):
      if board[x][y][1] == t:
        if board[x][y][0] == PAWN:
          if t==BLACK:
            if board[x+1][y][1] == NOCOLOR:
              if x==6:
                pawnPromote = [QUEEN, t], [BISHOP, t], [ROOK, t], [KNIGHT, t]
                for i in pawnPromote:
                  newBoards.append(copy.deepcopy(board))
                  newBoards[-1][x + 1][y] = copy.deepcopy(i)
                  newBoards[-1][x][y] = [NOTHING, NOCOLOR]
                  if inCheck(newBoards[-1], t):
                    newBoards.pop(-1)
              else:
                newBoards.append(copy.deepcopy(board))
                newBoards[-1][x + 1][y] = copy.deepcopy(
                    newBoards[-1][x][y])
                newBoards[-1][x][y] = [NOTHING, NOCOLOR]
                if inCheck(newBoards[-1], t):
                  newBoards.pop(-1)
            if x == 1:
              if board[x+1][y][1] == NOCOLOR and board[x+2][y][1] == NOCOLOR:
                newBoards.append(copy.deepcopy(board))
                newBoards[-1][x + 2][y] = copy.deepcopy(
                    newBoards[-1][x][y])
                newBoards[-1][x][y] = [NOTHING, NOCOLOR]
                if inCheck(newBoards[-1], t):
                  newBoards.pop(-1)
            if x == 4:
              if y<7:
                if all(board[x][y+1] == [PAWN, WHITE]) and all(board[6][y+1] == [NOTHING, NOCOLOR]) and all(prevBoard[6][y+1] == [PAWN, WHITE]):
                  newBoards.append(copy.deepcopy(board))
                  newBoards[-1][x + 1][y + 1] = copy.deepcopy(
                      newBoards[-1][x][y])
                  newBoards[-1][x][y] = [NOTHING, NOCOLOR]
                  newBoards[-1][x][y+1] = [NOTHING, NOCOLOR]
                  if inCheck(newBoards[-1], t):
                    newBoards.pop(-1)
              if y>0:
                if all(board[x][y-1] == [PAWN, WHITE]) and all(board[6][y-1] == [NOTHING, NOCOLOR]) and all(prevBoard[6][y-1] == [PAWN, WHITE]):
                  newBoards.append(copy.deepcopy(board))
                  newBoards[-1][x + 1][y - 1] = copy.deepcopy(
                      newBoards[-1][x][y])
                  newBoards[-1][x][y] = [NOTHING, NOCOLOR]
                  newBoards[-1][x][y-1] = [NOTHING, NOCOLOR]
                  if inCheck(newBoards[-1], t):
                    newBoards.pop(-1)
            if y<7:
              if board[x+1][y+1][1] == 3-t:
                if x==6:
                  pawnPromote = [QUEEN, t], [BISHOP, t], [ROOK, t], [KNIGHT, t]
                  for i in pawnPromote:
                    newBoards.append(copy.deepcopy(board))
                    newBoards[-1][x + 1][y + 1] = copy.deepcopy(i)
                    newBoards[-1][x][y] = [NOTHING, NOCOLOR]
                    if inCheck(newBoards[-1], t):
                      newBoards.pop(-1)
                else:
                  newBoards.append(copy.deepcopy(board))
                  newBoards[-1][x + 1][y + 1] = copy.deepcopy(
                      newBoards[-1][x][y])
                  newBoards[-1][x][y] = [NOTHING, NOCOLOR]
                  if inCheck(newBoards[-1], t):
                    newBoards.pop(-1)
            if y>0:
              if board[x+1][y-1][1] == 3-t:
                if x==6:
                  pawnPromote = [QUEEN, t], [BISHOP, t], [ROOK, t], [KNIGHT, t]
                  for i in pawnPromote:
                    newBoards.append(copy.deepcopy(board))
                    newBoards[-1][x + 1][y - 1] = copy.deepcopy(i)
                    newBoards[-1][x][y] = [NOTHING, NOCOLOR]
                    if inCheck(newBoards[-1], t):
                      newBoards.pop(-1)
                else:
                  newBoards.append(copy.deepcopy(board))
                  newBoards[-1][x + 1][y - 1] = copy.deepcopy(
                      newBoards[-1][x][y])
                  newBoards[-1][x][y] = [NOTHING, NOCOLOR]
                  if inCheck(newBoards[-1], t):
                    newBoards.pop(-1)
          else:
            if board[x-1][y][1] == NOCOLOR:
              if x==1:
                pawnPromote = [QUEEN, t], [BISHOP, t], [ROOK, t], [KNIGHT, t]
                for i in pawnPromote:
                  newBoards.append(copy.deepcopy(board))
                  newBoards[-1][x - 1][y] = copy.deepcopy(i)
                  newBoards[-1][x][y] = [NOTHING, NOCOLOR]
                  if inCheck(newBoards[-1], t):
                    newBoards.pop(-1)
              else:
                newBoards.append(copy.deepcopy(board))
                newBoards[-1][x - 1][y] = copy.deepcopy(
                    newBoards[-1][x][y])
                newBoards[-1][x][y] = [NOTHING, NOCOLOR]
                if inCheck(newBoards[-1], t):
                  newBoards.pop(-1)
            if x == 6:
              if board[x-1][y][1] == NOCOLOR and board[x-2][y][1] == NOCOLOR:
                newBoards.append(copy.deepcopy(board))
                newBoards[-1][x - 2][y] = copy.deepcopy(
                    newBoards[-1][x][y])
                newBoards[-1][x][y] = [NOTHING, NOCOLOR]
                if inCheck(newBoards[-1], t):
                  newBoards.pop(-1)
            if x == 3:
              if y<7:
                if all(board[x][y+1] == [PAWN, BLACK]) and all(board[1][y+1] == [NOTHING, NOCOLOR]) and all(prevBoard[1][y+1] == [PAWN, BLACK]):
                  newBoards.append(copy.deepcopy(board))
                  newBoards[-1][x - 1][y + 1] = copy.deepcopy(
                      newBoards[-1][x][y])
                  newBoards[-1][x][y] = [NOTHING, NOCOLOR]
                  newBoards[-1][x][y+1] = [NOTHING, NOCOLOR]
                  if inCheck(newBoards[-1], t):
                    newBoards.pop(-1)
              if y>0:
                if all(board[x][y-1] == [PAWN, BLACK]) and all(board[1][y-1] == [NOTHING, NOCOLOR]) and all(prevBoard[1][y-1] == [PAWN, BLACK]):
                  newBoards.append(copy.deepcopy(board))
                  newBoards[-1][x - 1][y - 1] = copy.deepcopy(
                      newBoards[-1][x][y])
                  newBoards[-1][x][y] = [NOTHING, NOCOLOR]
                  newBoards[-1][x][y-1] = [NOTHING, NOCOLOR]
                  if inCheck(newBoards[-1], t):
                    newBoards.pop(-1)
            if y<7:
              if board[x-1][y+1][1] == 3-t:
                if x==1:
                  pawnPromote = [QUEEN, t], [BISHOP, t], [ROOK, t], [KNIGHT, t]
                  for i in pawnPromote:
                    newBoards.append(copy.deepcopy(board))
                    newBoards[-1][x - 1][y + 1] = copy.deepcopy(i)
                    newBoards[-1][x][y] = [NOTHING, NOCOLOR]
                    if inCheck(newBoards[-1], t):
                      newBoards.pop(-1)
                else:
                  newBoards.append(copy.deepcopy(board))
                  newBoards[-1][x - 1][y + 1] = copy.deepcopy(
                      newBoards[-1][x][y])
                  newBoards[-1][x][y] = [NOTHING, NOCOLOR]
                  if inCheck(newBoards[-1], t):
                    newBoards.pop(-1)
            if y>0:
              if board[x-1][y-1][1] == 3-t:
                if x==1:
                  pawnPromote = [QUEEN, t], [BISHOP, t], [ROOK, t], [KNIGHT, t]
                  for i in pawnPromote:
                    newBoards.append(copy.deepcopy(board))
                    newBoards[-1][x - 1][y - 1] = copy.deepcopy(i)
                    newBoards[-1][x][y] = [NOTHING, NOCOLOR]
                    if inCheck(newBoards[-1], t):
                      newBoards.pop(-1)
                else:
                  newBoards.append(copy.deepcopy(board))
                  newBoards[-1][x - 1][y - 1] = copy.deepcopy(
                      newBoards[-1][x][y])
                  newBoards[-1][x][y] = [NOTHING, NOCOLOR]
                  if inCheck(newBoards[-1], t):
                    newBoards.pop(-1)
        elif board[x][y][0] == KNIGHT:
          knightMoves = [[1, 2], [1, -2], [-1, 2], [-1, -2], [2, 1], [2, -1],
                         [-2, 1], [-2, -1]]
          for i in knightMoves:
            if x + i[0] <= 7 and x + i[0] >= 0 and y + i[1] <= 7 and y + i[1] >= 0:
              if board[x + i[0]][y + i[1]][1] != t:
                newBoards.append(copy.deepcopy(board))
                newBoards[-1][x + i[0]][y + i[1]] = copy.deepcopy(
                    newBoards[-1][x][y])
                newBoards[-1][x][y] = [NOTHING, NOCOLOR]
                if inCheck(newBoards[-1], t):
                  newBoards.pop(-1)
        elif board[x][y][0] == BISHOP:
          bishopMoves = [zip(range(1, 8, 1), range(1, 8, 1)), zip(range(-1, -8, -1), range(1, 8, 1)), zip(range(-1, -8, -1), range(1, 8, 1)), zip(range(-1, -8, -1), range(-1, -8, -1))]
          for j in bishopMoves:
            for i in j:
              if x + i[0] <= 7 and x + i[0] >= 0 and y + i[1] <= 7 and y + i[1] >= 0:
                if board[x + i[0]][y + i[1]][1] == NOCOLOR:
                  newBoards.append(copy.deepcopy(board))
                  newBoards[-1][x + i[0]][y + i[1]] = copy.deepcopy(
                      newBoards[-1][x][y])
                  newBoards[-1][x][y] = [NOTHING, NOCOLOR]
                  if inCheck(newBoards[-1], t):
                    newBoards.pop(-1)
                elif board[x + i[0]][y + i[1]][1] == 3-t:
                  newBoards.append(copy.deepcopy(board))
                  newBoards[-1][x + i[0]][y + i[1]] = copy.deepcopy(
                      newBoards[-1][x][y])
                  newBoards[-1][x][y] = [NOTHING, NOCOLOR]
                  if inCheck(newBoards[-1], t):
                    newBoards.pop(-1)
                  break
                else:
                  break
        elif board[x][y][0] == ROOK:
          rookMoves = [zip(range(1, 8, 1), [0]*7), zip(range(-1, -8, -1), [0]*7), zip([0]*7, range(1, 8, 1)), zip([0]*7, range(-1, -8, -1))]
          for j in rookMoves:
            for i in j:
              if x + i[0] <= 7 and x + i[0] >= 0 and y + i[1] <= 7 and y + i[1] >= 0:
                if board[x + i[0]][y + i[1]][1] == NOCOLOR:
                  newBoards.append(copy.deepcopy(board))
                  newBoards[-1][x + i[0]][y + i[1]] = copy.deepcopy(
                      newBoards[-1][x][y])
                  newBoards[-1][x][y] = [NOTHING, NOCOLOR]
                  if inCheck(newBoards[-1], t):
                    newBoards.pop(-1)
                elif board[x + i[0]][y + i[1]][1] == 3-t:
                  newBoards.append(copy.deepcopy(board))
                  newBoards[-1][x + i[0]][y + i[1]] = copy.deepcopy(
                      newBoards[-1][x][y])
                  newBoards[-1][x][y] = [NOTHING, NOCOLOR]
                  if inCheck(newBoards[-1], t):
                    newBoards.pop(-1)
                  break
                else:
                  break
        elif board[x][y][0] == QUEEN:
          # Both rook and bishop moves
          bishopMoves = [zip(range(1, 8, 1), range(1, 8, 1)), zip(range(-1, -8, -1), range(1, 8, 1)), zip(range(-1, -8, -1), range(1, 8, 1)), zip(range(-1, -8, -1), range(-1, -8, -1))]
          for j in bishopMoves:
            for i in j:
              if x + i[0] <= 7 and x + i[0] >= 0 and y + i[1] <= 7 and y + i[1] >= 0:
                if board[x + i[0]][y + i[1]][1] == NOCOLOR:
                  newBoards.append(copy.deepcopy(board))
                  newBoards[-1][x + i[0]][y + i[1]] = copy.deepcopy(
                      newBoards[-1][x][y])
                  newBoards[-1][x][y] = [NOTHING, NOCOLOR]
                  if inCheck(newBoards[-1], t):
                    newBoards.pop(-1)
                elif board[x + i[0]][y + i[1]][1] == 3-t:
                  newBoards.append(copy.deepcopy(board))
                  newBoards[-1][x + i[0]][y + i[1]] = copy.deepcopy(
                      newBoards[-1][x][y])
                  newBoards[-1][x][y] = [NOTHING, NOCOLOR]
                  if inCheck(newBoards[-1], t):
                    newBoards.pop(-1)
                  break
                else:
                  break
          rookMoves = [zip(range(1, 8, 1), [0]*7), zip(range(-1, -8, -1), [0]*7), zip([0]*7, range(1, 8, 1)), zip([0]*7, range(-1, -8, -1))]
          for j in rookMoves:
            for i in j:
              if x + i[0] <= 7 and x + i[0] >= 0 and y + i[1] <= 7 and y + i[1] >= 0:
                if board[x + i[0]][y + i[1]][1] == NOCOLOR:
                  newBoards.append(copy.deepcopy(board))
                  newBoards[-1][x + i[0]][y + i[1]] = copy.deepcopy(
                      newBoards[-1][x][y])
                  newBoards[-1][x][y] = [NOTHING, NOCOLOR]
                  if inCheck(newBoards[-1], t):
                    newBoards.pop(-1)
                elif board[x + i[0]][y + i[1]][1] == 3-t:
                  newBoards.append(copy.deepcopy(board))
                  newBoards[-1][x + i[0]][y + i[1]] = copy.deepcopy(
                      newBoards[-1][x][y])
                  newBoards[-1][x][y] = [NOTHING, NOCOLOR]
                  if inCheck(newBoards[-1], t):
                    newBoards.pop(-1)
                  break
                else:
                  break
        else:
          kingMoves = [[1, 1], [1, -1], [-1, 1], [-1, -1], [0, 1], [0, -1], [1, 0], [-1, 0]]
          for i in kingMoves:
            if x + i[0] <= 7 and x + i[0] >= 0 and y + i[1] <= 7 and y + i[1] >= 0:
              if board[x + i[0]][y + i[1]][1] != t:
                newBoards.append(copy.deepcopy(board))
                newBoards[-1][x + i[0]][y + i[1]] = copy.deepcopy(
                    newBoards[-1][x][y])
                newBoards[-1][x][y] = [NOTHING, NOCOLOR]
                if inCheck(newBoards[-1], t):
                  newBoards.pop(-1)
  return newBoards

def algoDecide(board, t, depth):  # Run a recursive algorithm to find the best move
  global boardToEvalAlgo
  global prevBoard
  
  prevBoard2 = copy.deepcopy(prevBoard)

  if isCheckmate(board,  t):  # If it's checkmate, return who won and the position
    if t == BLACK:
      return (2, board)
    else:
      return (-2, board)
  elif isStalemate(board, t):  # If it's stalemate, return the position and a draw
    return (0, board)
  
  if depth == 0:  # If it should not look in the future, evaluate the position
    boardAsTuple = deepTuple(board)
    if boardAsTuple in boardToEvalAlgo:  # If the algo already calculated it, use that value
      return (boardToEvalAlgo[boardAsTuple], board)
    boardEval = evaluatePos(board)
    # Scale the evaluation from -0.9 to 0.9 and return it with the board
    return (max(-1.9, min(boardEval / 12, 1.9)), board)

  # Look at all the moves and check which one is the best move
  getEval = lambda board: board[0]
  if t == BLACK:  # If the turn is black, look for the move with the lowest value
    getEval = lambda board: board[0] * -1
  arr = [(algoDecide(i, 3 - t, depth - 1)[0], i) if deepTuple(i) not in prevMoves else (algoDecide(i, 3 - t, depth - 1)[0]*0.2, i) for i in getPossibleMoves(board, t)]
  bestMove = max(arr, key=getEval)

  # If the move hasn't been stored, store it in the dictionary and the file
  if depth>=algoDepth-1:
    moveAsTuple = deepTuple(bestMove[1])
    fileAddData(bestMove[1], bestMove[0])
    boardToEvalAlgo[moveAsTuple] = bestMove[0]
  
  prevBoard = copy.deepcopy(prevBoard2)

  return bestMove

def mlDecide(board, t, depth):  # Runs the ML algorithm to generate the move
  mlDecision = chessBoard  # ADD ML PREDICTION HERE

  # If the move is valid, run it, otherwise run the algorithm to decide the move
  if mlDecision in getPossibleMoves(board, t):
    return mlDecision
  return algoDecide(board, t, depth)[1]


# Defines constant vairables below

# Stores the key of each piece for better code readability
NOTHING, PAWN, BISHOP, KNIGHT, ROOK, QUEEN, KING = 0, 1, 2, 3, 4, 5, 6

# Maps the piece to the points it is worth
VALUES = {
    NOTHING: 0,
    PAWN: 1,
    BISHOP: 3,
    KNIGHT: 3,
    ROOK: 5,
    QUEEN: 19,
    KING: 1000
}

# Stores the key of each color for better readability
NOCOLOR, WHITE, BLACK = 0, 1, 2
PLAYER, ALGO, ML = 0, 1, 2

# Stores the depth of the algorithm
algoDepth = 3

# Defines non-constant variables below
turn = WHITE

# Stores which color is which player
order = {
    WHITE: PLAYER,
    BLACK: PLAYER
}  # Depending on game configuration, this can change

# Creates the inital starting board
chessBoard = np.array([
    [np.array([piece, BLACK]) for piece in [4, 3, 2, 5, 6, 2, 3, 4]],
    [np.array([PAWN, BLACK])] * 8,
    [np.array([NOTHING, NOCOLOR])] * 8,
    [np.array([NOTHING, NOCOLOR])] * 8,
    [np.array([NOTHING, NOCOLOR])] * 8,
    [np.array([NOTHING, NOCOLOR])] * 8,
    [np.array([PAWN, WHITE])] * 8,
    [np.array([piece, WHITE]) for piece in [4, 3, 2, 5, 6, 2, 3, 4]],
])


# Dictionary to store the previous moves
prevMoves = {}

# Stores the last board position
prevBoard = copy.deepcopy(chessBoard)

# Reads data from the file to a dictionary storing the evaluation of boards
dataFileAlgo = open("dataStorageAlgo.txt", "r")
boardToEvalAlgo = {
    deepTuple(boardFromNums(line.split(" ")[:-1])): float(line.split(" ")[-1])
    for line in dataFileAlgo.readlines()
}
dataFileAlgo.close()

# Open the file to add more data
def m(x):
  if x[1]==WHITE:
    if x[0]==KING:
      return "♔"
    if x[0]==QUEEN:
      return "♕"
    if x[0]==ROOK:
      return "♖"
    if x[0]==BISHOP:
      return "♗"
    if x[0]==KNIGHT:
      return "♘"
    if x[0]==PAWN:
      return "♙"
  elif x[1]==BLACK:
    if x[0]==KING:
      return "♚"
    if x[0]==QUEEN:
      return "♛"
    if x[0]==ROOK:
      return "♜"
    if x[0]==BISHOP:
      return "♝"
    if x[0]==KNIGHT:
      return "♞"
    if x[0]==PAWN:
      return "♟︎"
  return " "
dataFileAlgo = open("dataStorageAlgo.txt", "a")
print (u"\u001b[47m")

while True:
  makeMove(algoDecide(chessBoard, turn, algoDepth)[1])
  print()
  for i in [chessBoard]:
      for j in i:
        print(" , ".join([m(x) for x in j]))
  if isCheckmate(chessBoard, turn):
    print(str(3-turn) + " Wins!!")
    break
  elif isStalemate(chessBoard, turn):
    print("Tie!!")
    break
  print("{:0.2f}".format(evaluatePos(chessBoard)))

dataFileAlgo.close()

exit(1)
# Runs game below
pg.init()
pg.display.set_mode((500, 500))
pg.display.set_caption("Chess")

while True:

  if order[turn] == PLAYER:
    print("Player's Turn")
  elif order[turn] == ALGO:
    makeMove(algoDecide(chessBoard, turn, 3)[1])
    print("Algorithm's Turn")
  else:
    makeMove(mlDecide(chessBoard, turn, 3))
    print("ML model's Turn")

  chessBoardTuple = tuple(tuple(tuple(j) for j in i) for i in chessBoard)
  if tuple(chessBoardTuple) in prevMoves:
    prevMoves[chessBoardTuple] += 1
  else:
    prevMoves[chessBoardTuple] = 1

  if isCheckmate(chessBoard, turn):
    print(str(turn) + " Wins!!")
    break
  elif isStalemate(chessBoard, turn):
    print("Tie!!")
    break

  print("Update Screen")

dataFileAlgo.close()
