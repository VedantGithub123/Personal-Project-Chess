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

# Defines functions below
def boardFromNums(nums):  # Creates a board from a list of strings
  # Converts the list into a list of ints and reshapes it into a 3D np array
  return np.array(list(map(int, nums))).reshape((8, 8, 2))

def boardToStr(board):
  return " ".join(map(str, board.flatten()))

def fileAddData(board, eval):  # Writes the board to a file in a certain format
  # Flattens the board and joins it with a " " between the different values
  dataFileAlgo.write(board + " | " + str(eval) + "\n")

def makeMove(move):  # Changes the chessboard and swaps the turn
  # Says we are changing the global vairables instead of new ones in a smaller scope
  global chessBoard
  global turn
  global prevBoard
  global prevCaptureLen
  global castleShort
  global castleLong
  global boardFlip

  turn = 3 - turn

  boardAsStr = boardToStr(chessBoard)
  if boardAsStr in prevMoves:
    prevMoves[boardAsStr] += 1
  else:
    prevMoves[boardAsStr] = 1

  prevCaptureLen+=1

  if pointSum(move)!=pointSum(chessBoard):
    prevCaptureLen = 0

  prevBoard = copy.deepcopy(chessBoard)

  for col, row in [[WHITE, 7], [BLACK, 0]]:
    if not all(move[row][0]==[ROOK, col]):
      castleLong[col] = False
    if not all(move[row][7]==[ROOK, col]):
      castleShort[col] = False
    if not all(move[row][4]==[KING, col]):
        castleLong[col] = False
        castleShort[col] = False

  if order[BLACK]!=PLAYER:
    boardFlip = False
  elif order[WHITE]!=PLAYER:
    boardFlip = True
  else:
    boardFlip = True if turn==BLACK else False
  
  chessBoard = copy.deepcopy(move)
  
def evaluatePos(board):  # Uses points to evaulate the position of the board
  # Adds together the different point values, subtracts if black's pieces
  boardAsStr = boardToStr(board)
  if boardAsStr in boardToEvalAlgo:  # If the algo already calculated it, use that value
    return boardToEvalAlgo[boardAsStr]
  sum = 0
  for x, i in enumerate(board):
    for y, j in enumerate(i):
      val = lambda x: x
      if j[1] == BLACK:
        val = lambda x: -1*x
      
      addVal = val(VALUES[j[0]])*(1.035-abs(x-3.5)/50)*(1.035-abs(y-3.5)/50)
      if j[0] == PAWN:
        addVal*=(0.005*(x if j[1]==BLACK else 7-x)+0.9625)
      
      if j[0] != KING:
        sum+=addVal
  sum *= (1.039-(pointSum(board)-VALUES[KING]*2)/1000)
  return max(-0.9, min(sum / 200, 0.9))

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
        # Checks if a rook, bishop, or queen is attacking the king
        for moves, piece in [[rookMoves, ROOK], [bishopMoves, BISHOP]]:
          for line in moves:
            for i in line:
              if x + i[0] <= 7 and x + i[0] >= 0 and y + i[1] <= 7 and y + i[1] >= 0:
                if board[x + i[0]][y + i[1]][1] != t and board[x + i[0]][y + i[1]][0] in [piece, QUEEN]:
                  return True
                elif board[x + i[0]][y + i[1]][0] != NOTHING:
                  break
        
        # Checks if a knight or king is attacking the king
        for moves, piece in [[knightMoves, KNIGHT], [kingMoves, KING]]:
          for i in moves:
            if x+i[0]>=0 and x+i[0]<8 and y+i[1]>=0 and y+i[1]<8:
              if board[x+i[0]][y+i[1]][1]==3-t and board[x+i[0]][y+i[1]][0] == piece:
                return True

        # Checks if a pawn is attacking the king
        xAdd = (1 if t==BLACK else -1)
        for yAdd in [1, -1]:
          if x+xAdd>=0 and x+xAdd<=7 and y+yAdd<=7 and y+yAdd>=0:
            if board[x+xAdd][y+yAdd][0] == PAWN and board[x+xAdd][y+yAdd][1] == 3-t:
              return True
            
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
          or prevCaptureLen>=50
          or pointSum(board) == VALUES[KING] + VALUES[KING]
          or (pointSum(board) == VALUES[KING] + VALUES[KING] + VALUES[KNIGHT] and all(i[0]!=PAWN for i in board)) # Same as KING+KING+BISHOP
          )

def getPossibleMoves(board, t):
  newBoards = []
  for y in range(8):
    for x in range(8):
      newBoards += [i[1] for i in getPossiblePositions(board, x, y, t)]
  return newBoards

def getPossibleCoordinates(board, x, y, t):
  return [i[0] for i in getPossiblePositions(board, x, y, t)]

def getPieceMoves(board, x, y, t):
  return [i[1] for i in getPossiblePositions(board, x, y, t)]

def algoDecide(board, t, depth):  # Run a recursive algorithm to find the best move
  global boardToEvalAlgo
  global prevBoard
  global prevCaptureLen
  global prevMoves
  global castleShort
  global castleLong

  if isCheckmate(board,  t):  # If it's checkmate, return who won and the position
    if t == BLACK:
      return (1, board)
    else:
      return (-1, board)
  elif isStalemate(board, t):  # If it's stalemate, return the position and a draw
    return (0, board)
  
  if depth == 0:  # If it should not look in the future, evaluate the position
    return (evaluatePos(board), board)
  
  prevMoves2 = prevMoves.copy()
  castleLong2 = castleLong.copy()
  castleShort2 = castleShort.copy()
  prevBoard2 = copy.deepcopy(prevBoard)
  prevCaptureLen2 = prevCaptureLen
  
  boardAsStr = boardToStr(board)
  if boardAsStr in prevMoves:
    prevMoves[boardAsStr] += 1
  else:
    prevMoves[boardAsStr] = 1

  prevCaptureLen+=1
  if pointSum(board)!=pointSum(prevBoard):
    prevCaptureLen = 0

  prevBoard = copy.deepcopy(board)

  if not all(board[0][0]==[ROOK, BLACK]):
    castleLong[BLACK] = False
  if not all(board[7][0]==[ROOK, WHITE]):
    castleLong[WHITE] = False
  if not all(board[0][7]==[ROOK, BLACK]):
    castleShort[BLACK] = False
  if not all(board[7][7]==[ROOK, WHITE]):
    castleShort[WHITE] = False
  if not all(board[0][4]==[KING, BLACK]):
      castleLong[BLACK] = False
      castleShort[BLACK] = False
  if not all(board[7][4]==[KING, WHITE]):
      castleLong[WHITE] = False
      castleShort[WHITE] = False

  # Look at all the moves and check which one is the best move
  getEval = lambda board: board[0]
  if t == BLACK:  # If the turn is black, look for the move with the lowest value
    getEval = lambda board: board[0] * -1
  arr = [(algoDecide(i, 3 - t, depth - 1)[0], i) if boardToStr(i) not in prevMoves else (algoDecide(i, 3 - t, depth - 1)[0]*0.5, i)
         for i in getPossibleMoves(board, t)]
  bestMove = max(arr, key=getEval)

  prevMoves = prevMoves2.copy()
  castleShort = castleShort2.copy()
  castleLong = castleLong2.copy()
  prevCaptureLen = prevCaptureLen2
  prevBoard = copy.deepcopy(prevBoard2)

  # If the move hasn't been stored, store it in the dictionary and the file
  if depth>algoDepth-1:
    moveAsStr = boardToStr(bestMove[1])
    boardToEvalAlgo[moveAsStr] = bestMove[0]

  return bestMove

def mlDecide(board, t, depth):  # Runs the ML algorithm to generate the move
  mlDecision = chessBoard  # ADD ML PREDICTION HERE

  # If the move is valid, run it, otherwise run the algorithm to decide the move
  if mlDecision in getPossibleMoves(board, t):
    return mlDecision
  return algoDecide(board, t, depth)[1]

def resetBoard():
  global algoDepth
  global turn
  global order
  global chessBoard
  global prevMoves
  global prevBoard
  global prevCaptureLen
  global castleLong
  global castleShort

  algoDepth = 3

  turn = WHITE

  order = {
    WHITE: PLAYER,
    BLACK: PLAYER
  }

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

  prevMoves = {}

  prevBoard = copy.deepcopy(chessBoard)

  prevCaptureLen = 0

  castleLong = {
    WHITE: True,
    BLACK: True
  }

  castleShort = {
    WHITE: True,
    BLACK: True
  }

def getPossiblePositions(board, x, y, t):
  newBoards = []
  newCoordinates = []
  if board[x][y][1]!=t:
    return []
  
  piece = board[x][y][0]
  if piece==PAWN:
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
              newCoordinates.append((x+1, y))
        else:
          newBoards.append(copy.deepcopy(board))
          newBoards[-1][x + 1][y] = copy.deepcopy(
              newBoards[-1][x][y])
          newBoards[-1][x][y] = [NOTHING, NOCOLOR]
          if inCheck(newBoards[-1], t):
            newBoards.pop(-1)
          else:
            newCoordinates.append((x+1, y))
      if x == 1:
        if board[x+1][y][1] == NOCOLOR and board[x+2][y][1] == NOCOLOR:
          newBoards.append(copy.deepcopy(board))
          newBoards[-1][x + 2][y] = copy.deepcopy(
              newBoards[-1][x][y])
          newBoards[-1][x][y] = [NOTHING, NOCOLOR]
          if inCheck(newBoards[-1], t):
            newBoards.pop(-1)
          else:
            newCoordinates.append((x+2, y))
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
            else:
              newCoordinates.append((x+1, y+1))
        if y>0:
          if all(board[x][y-1] == [PAWN, WHITE]) and all(board[6][y-1] == [NOTHING, NOCOLOR]) and all(prevBoard[6][y-1] == [PAWN, WHITE]):
            newBoards.append(copy.deepcopy(board))
            newBoards[-1][x + 1][y - 1] = copy.deepcopy(
                newBoards[-1][x][y])
            newBoards[-1][x][y] = [NOTHING, NOCOLOR]
            newBoards[-1][x][y-1] = [NOTHING, NOCOLOR]
            if inCheck(newBoards[-1], t):
              newBoards.pop(-1)
            else:
              newCoordinates.append((x+1, y-1))
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
              newCoordinates.append((x+1, y+1))
          else:
            newBoards.append(copy.deepcopy(board))
            newBoards[-1][x + 1][y + 1] = copy.deepcopy(
                newBoards[-1][x][y])
            newBoards[-1][x][y] = [NOTHING, NOCOLOR]
            if inCheck(newBoards[-1], t):
              newBoards.pop(-1)
            else:
              newCoordinates.append((x+1, y+1))
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
                newCoordinates.append((x+1, y-1))
          else:
            newBoards.append(copy.deepcopy(board))
            newBoards[-1][x + 1][y - 1] = copy.deepcopy(
                newBoards[-1][x][y])
            newBoards[-1][x][y] = [NOTHING, NOCOLOR]
            if inCheck(newBoards[-1], t):
              newBoards.pop(-1)
            else:
              newCoordinates.append((x+1, y-1))
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
              newCoordinates.append((x-1, y))
        else:
          newBoards.append(copy.deepcopy(board))
          newBoards[-1][x - 1][y] = copy.deepcopy(
              newBoards[-1][x][y])
          newBoards[-1][x][y] = [NOTHING, NOCOLOR]
          if inCheck(newBoards[-1], t):
            newBoards.pop(-1)
          else:
            newCoordinates.append((x-1, y))
      if x == 6:
        if board[x-1][y][1] == NOCOLOR and board[x-2][y][1] == NOCOLOR:
          newBoards.append(copy.deepcopy(board))
          newBoards[-1][x - 2][y] = copy.deepcopy(
              newBoards[-1][x][y])
          newBoards[-1][x][y] = [NOTHING, NOCOLOR]
          if inCheck(newBoards[-1], t):
            newBoards.pop(-1)
          else:
            newCoordinates.append((x-2, y))
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
            else:
              newCoordinates.append((x-1, y+1))
        if y>0:
          if all(board[x][y-1] == [PAWN, BLACK]) and all(board[1][y-1] == [NOTHING, NOCOLOR]) and all(prevBoard[1][y-1] == [PAWN, BLACK]):
            newBoards.append(copy.deepcopy(board))
            newBoards[-1][x - 1][y - 1] = copy.deepcopy(
                newBoards[-1][x][y])
            newBoards[-1][x][y] = [NOTHING, NOCOLOR]
            newBoards[-1][x][y-1] = [NOTHING, NOCOLOR]
            if inCheck(newBoards[-1], t):
              newBoards.pop(-1)
            else:
              newCoordinates.append((x-1, y-1))
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
              newCoordinates.append((x-1, y+1))
          else:
            newBoards.append(copy.deepcopy(board))
            newBoards[-1][x - 1][y + 1] = copy.deepcopy(
                newBoards[-1][x][y])
            newBoards[-1][x][y] = [NOTHING, NOCOLOR]
            if inCheck(newBoards[-1], t):
              newBoards.pop(-1)
            else:
              newCoordinates.append((x-1, y+1))
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
              newCoordinates.append((x-1, y-1))
          else:
            newBoards.append(copy.deepcopy(board))
            newBoards[-1][x - 1][y - 1] = copy.deepcopy(
                newBoards[-1][x][y])
            newBoards[-1][x][y] = [NOTHING, NOCOLOR]
            if inCheck(newBoards[-1], t):
              newBoards.pop(-1)
            else:
              newCoordinates.append((x-1, y-1))
  
  for moves, piece2 in [[bishopMoves, BISHOP], [rookMoves, ROOK]]:
    if piece in [piece2, QUEEN]:
      for line in moves:
        for i in line:
          if x + i[0] <= 7 and x + i[0] >= 0 and y + i[1] <= 7 and y + i[1] >= 0:
            if board[x + i[0]][y + i[1]][1] != t:
              newBoards.append(copy.deepcopy(board))
              newBoards[-1][x + i[0]][y + i[1]] = copy.deepcopy(
                  newBoards[-1][x][y])
              newBoards[-1][x][y] = [NOTHING, NOCOLOR]
              if inCheck(newBoards[-1], t):
                newBoards.pop(-1)
              else:
                newCoordinates.append((x+i[0], y+i[1]))
            if board[x + i[0]][y + i[1]][1] != NOTHING:
              break
  
  for moves, piece2 in [[knightMoves, KNIGHT], [kingMoves, KING]]:
    if piece == piece2:
      for i in moves:
        if x + i[0] <= 7 and x + i[0] >= 0 and y + i[1] <= 7 and y + i[1] >= 0:
          if board[x + i[0]][y + i[1]][1] != t:
            newBoards.append(copy.deepcopy(board))
            newBoards[-1][x + i[0]][y + i[1]] = copy.deepcopy(
                newBoards[-1][x][y])
            newBoards[-1][x][y] = [NOTHING, NOCOLOR]
            if inCheck(newBoards[-1], t):
              newBoards.pop(-1)
            else:
              newCoordinates.append((x+i[0], y+i[1]))
  
  row = 0
  if t==WHITE:
    row = 7
  if castleLong[t] and not inCheck(board, t) and all(board[row][1]==[NOTHING, NOCOLOR]) and all(board[row][2]==[NOTHING, NOCOLOR]) and all(board[row][3]==[NOTHING, NOCOLOR]):
    copyBoard = copy.deepcopy(board)
    copyBoard[row][2]=np.array([KING, t])
    copyBoard[row][4]=np.array([NOTHING, NOCOLOR])
    if not inCheck(copyBoard, t):
      copyBoard = copy.deepcopy(board)
      copyBoard[row][3]=np.array([KING, t])
      copyBoard[row][4]=np.array([NOTHING, NOCOLOR])
      if not inCheck(copyBoard, t):
        copyBoard = copy.deepcopy(board)
        copyBoard[row][2]=np.array([KING, t])
        copyBoard[row][3]=np.array([ROOK, t])
        copyBoard[row][4]=np.array([NOTHING, NOCOLOR])
        copyBoard[row][0]=np.array([NOTHING, NOCOLOR])
        newBoards.append(copy.deepcopy(copyBoard))
        newCoordinates.append((row, 2))

  if castleShort[t] and not inCheck(board, t) and all(board[row][5]==[NOTHING, NOCOLOR]) and all(board[row][6]==[NOTHING, NOCOLOR]):
    copyBoard = copy.deepcopy(board)
    copyBoard[row][6]=np.array([KING, t])
    copyBoard[row][4]=np.array([NOTHING, NOCOLOR])
    if not inCheck(copyBoard, t):
      copyBoard = copy.deepcopy(board)
      copyBoard[row][6]=np.array([KING, t])
      copyBoard[row][4]=np.array([NOTHING, NOCOLOR])
      if not inCheck(copyBoard, t):
        copyBoard = copy.deepcopy(board)
        copyBoard[row][6]=np.array([KING, t])
        copyBoard[row][5]=np.array([ROOK, t])
        copyBoard[row][7]=np.array([NOTHING, NOCOLOR])
        copyBoard[row][4]=np.array([NOTHING, NOCOLOR])
        newBoards.append(copy.deepcopy(copyBoard))
        newCoordinates.append((row, 6))
  
  return list(zip(newCoordinates, newBoards))

def updateScreenBoard():
  screen.fill((83, 92, 86))

  image = pg.image.load("images\\chessboard.jpg").convert()
  image = pg.transform.scale(image, (720, 720))
  screen.blit(image, (0, 0))

  image = pg.image.load("images\\title.png").convert_alpha()
  image = pg.transform.scale(image, (612, 408))
  screen.blit(image, (694, -120))

  for x, v in enumerate(chessBoard[::(-1 if boardFlip else 1)]):
    for y, w in enumerate(v[::(-1 if boardFlip else 1)]):
      if any(w!=[0, 0]):
        image = pg.image.load("images\\"+"".join([str(i) for i in w])+".svg")
        screen.blit(image, (90*y, 90*x))
  
  if selectedX != -1 and selectedY != -1 and chessBoard[selectedX][selectedY][1] == turn and order[turn]==PLAYER and gameStarted:
    image = pg.image.load("images\\select.png").convert_alpha()
    image = pg.transform.scale(image, (90, 90))
    if boardFlip:
      screen.blit(image, (90*(7-selectedY), 90*(7-selectedX)))
    else:
      screen.blit(image, (90*(selectedY), 90*(selectedX)))
    for x, y in getPossibleCoordinates(chessBoard, selectedX, selectedY, turn):
      if boardFlip:
        x = 7-x
        y = 7-y
      image = pg.image.load("images\\select.png").convert_alpha()
      image = pg.transform.scale(image, (70, 70))
      screen.blit(image, (90*y+10, 90*x+10))

  pg.display.flip()

def coordinateToXY(clickTuple):
  y = int(clickTuple[0]/90)
  x = int(clickTuple[1]/90)
  if x<8 and y<8:
    if boardFlip:
      return (7-x, 7-y)
    return (x, y)
  return (-1, -1)

########################################################################################

# Defines constant vairables below
# These vairables are used for reference in the rest of the code for better readability

# Stores the key of each piece for better code readability
NOTHING, PAWN, BISHOP, KNIGHT, ROOK, QUEEN, KING = 0, 1, 2, 3, 4, 5, 6

# Maps the piece to the points it is worth
VALUES = {
    NOTHING: 0,
    PAWN: 1,
    BISHOP: 3,
    KNIGHT: 3,
    ROOK: 5,
    QUEEN: 9,
    KING: 1000
}

# Stores the key of each color for better readability
NOCOLOR, WHITE, BLACK = 0, 1, 2
PLAYER, ALGO, ML = 0, 1, 2

# Stores the height and width of the screen
HEIGHT, WIDTH = 720, 1260

# Stores the possible moves a knight can make
knightMoves = [[1, 2], [1, -2], [-1, 2], [-1, -2], [2, 1], [2, -1], [-2, 1], [-2, -1]]

# Stores the possible moves a bishop can make
bishopMoves = [zip(range(1, 8, 1), range(1, 8, 1)), zip(range(-1, -8, -1), range(1, 8, 1)), zip(range(1, 8, 1), range(-1, -8, -1)), zip(range(-1, -8, -1), range(-1, -8, -1))]
bishopMoves = list(map(list, bishopMoves))

# Stores the possible moves a rook can make
rookMoves = [zip(range(1, 8, 1), [0]*7), zip(range(-1, -8, -1), [0]*7), zip([0]*7, range(1, 8, 1)), zip([0]*7, range(-1, -8, -1))]
rookMoves = list(map(list, rookMoves))

# Stores the possible moves a king can make
kingMoves = [[1, 1], [1, -1], [-1, 1], [-1, -1], [0, 1], [0, -1], [1, 0], [-1, 0]]


########################################################################################

# Defines non-constant variables below

# Reads data from the file to a dictionary storing the evaluation of boards
dataFileAlgo = open("dataStorageAlgo.txt", "r")
boardToEvalAlgo = {
    # Formatted input board | evaluation
    line.split(" | ")[0]: float(line.split(" | ")[1])
    for line in dataFileAlgo.readlines()
}
dataFileAlgo.close()


# Stores the current turn
turn = WHITE

# Stores the depth of the algorithm
algoDepth = 3

# Stores which color is which player
order = {
    WHITE: PLAYER,
    BLACK: PLAYER
}  # Depending on game configuration, this can change

castleLong = {
  WHITE: True,
  BLACK: True
}

castleShort = {
  WHITE: True,
  BLACK: True
}

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

# Vairable to store the number of moves since the last capture or pawn move
prevCaptureLen = 0

########################################################################################

# Defines UI vairables below

# Variables to hold the last xy click of the user to show the possible moves
selectedX = -1
selectedY = -1

# Variable to store if the board should be flipped
boardFlip = False

# Variable to store if the game has started
gameStarted = True


pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Chess")
running = True
while running:
  for event in pg.event.get():
    if event.type == pg.QUIT:
      running = False
    if event.type == pg.MOUSEBUTTONUP:
      if selectedX != -1:
        if coordinateToXY(pg.mouse.get_pos()) in getPossibleCoordinates(chessBoard, selectedX, selectedY, turn):
          index = getPossibleCoordinates(chessBoard, selectedX, selectedY, turn).index(coordinateToXY(pg.mouse.get_pos()))
          makeMove(getPieceMoves(chessBoard, selectedX, selectedY, turn)[index])
        selectedX, selectedY = -1, -1
      else:
        newCoordinate = coordinateToXY(pg.mouse.get_pos())
        if chessBoard[newCoordinate[0]][newCoordinate[1]][1]==turn:
          selectedX = newCoordinate[0]
          selectedY = newCoordinate[1]
  updateScreenBoard()

dataFileAlgo = open("dataStorageAlgo.txt", "w")
for i in boardToEvalAlgo:
  fileAddData(i, boardToEvalAlgo[i])
dataFileAlgo.close()

exit(1)

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

for lasd in range(1):
  resetBoard()
  moveCount = 0
  print (u"\u001b[47m")
  while True:
    moveCount+=1
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
    print("{:0.2f}".format(evaluatePos(chessBoard)*10))
    print(moveCount)

  dataFileAlgo = open("dataStorageAlgo.txt", "w")
  for i in boardToEvalAlgo:
    fileAddData(i, boardToEvalAlgo[i])
  dataFileAlgo.close()


# Runs game below

pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))

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
  if isCheckmate(chessBoard, turn):
    print(str(turn) + " Wins!!")
    break
  elif isStalemate(chessBoard, turn):
    print("Tie!!")
    break

  print("Update Screen")

dataFileAlgo.close()
