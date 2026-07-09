import pygame
import random
import json

# region Import data
with open("settings.json") as json_data:
    data = json.load(json_data)

# region Basic classes
class Piece:
    I = 1
    O = 2
    T = 3
    S = 4
    Z = 5
    J = 6
    L = 7

PIECE = [Piece.I, Piece.O, Piece.T, Piece.S, Piece.Z, Piece.J, Piece.L]

class Mino:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __add__(self, other: "Mino") -> "Mino":
        if isinstance(other, Mino):
            return Mino(self.x + other.x, self.y + other.y)
        return NotImplemented
    
    def __sub__(self, other: "Mino") -> "Mino":
        if isinstance(other, Mino):
            return Mino(self.x - other.x, self.y - other.y)
        return NotImplemented
    
    def __mul__(self, other: int) -> "Mino":
        if isinstance(other, int):
            return Mino(self.x * other, self.y * other)
        return NotImplemented

    def __eq__(self, other: "Mino") -> bool:
        if isinstance(other, Mino):
            return (self.x == other.x) and (self.y == other.y)
        return NotImplemented

    def __repr__(self):
        return f'Mino({self.x} {self.y})'
    
class Offset(list):
    def __add__(self, other: "Offset | Mino") -> "Offset":
        if isinstance(other, Mino):
            return Offset([x+other for x in self])
        
        elif isinstance(other, Offset):
            if len(self) != len(other):
                raise ValueError("Offsets must have the same length")
            return Offset([a+b for a, b in zip(self, other)])
        
        return NotImplemented
    
    def __sub__(self, other: "Offset | Mino") -> "Offset":
        if isinstance(other, Mino):
            return Offset([x-other for x in self])
        
        elif isinstance(other, Offset):
            if len(self) != len(other):
                raise ValueError("Offsets must have the same length")
            return Offset([a-b for a, b in zip(self, other)])
        
        return NotImplemented
    
    def __repr__(self):
        return f'Offset({list(self)})'

# endregion

# region Constants and variables

# Board
boardHeight: int = 23
boardWidth: int = 10
playingHeight: int = 20
SPAWN_POSITION = Mino((boardWidth+1)//2-1, playingHeight)

death = False
MINO_SIZE = 32
SIDE_BUFFER = 150
BOARD_THICKNESS = 5
WIDTH = MINO_SIZE * boardWidth + (SIDE_BUFFER + BOARD_THICKNESS) * 2
HEIGHT = MINO_SIZE * boardHeight + BOARD_THICKNESS
SCREEN = (WIDTH, HEIGHT)
PREVIEW_SIZE = 5

# Handling
DAS = data['DAS']
ARR = data['ARR']
SDF = data['SDF']

DAShorizontal = -DAS
DASdirection = 0
DASdown = -SDF

NAME = ["NULL", "I", "O", "T", "S", "Z", "J", "L"]

# Color palette
COLORS = {
    0: (20, 20, 20),
    Piece.I: (25, 235, 235),
    Piece.O: (235, 235, 25),
    Piece.T: (145, 25, 210),
    Piece.S: (25, 235, 25),
    Piece.Z: (235, 25, 25),
    Piece.J: (25, 25, 235),
    Piece.L: (235, 96, 25),
}

# Spawn shape
SHAPE = {
    Piece.I: [Mino(0, 0), Mino(-1, 0), Mino(1, 0), Mino(2, 0)],
    Piece.O: [Mino(0, 0), Mino(1, 0), Mino(0, 1), Mino(1, 1)],
    Piece.T: [Mino(0, 0), Mino(-1, 0), Mino(0, 1), Mino(1, 0)],
    Piece.S: [Mino(0, 0), Mino(-1, 0), Mino(0, 1), Mino(1, 1)],
    Piece.Z: [Mino(0, 0), Mino(1, 0), Mino(0, 1), Mino(-1, 1)],
    Piece.J: [Mino(0, 0), Mino(-1, 0), Mino(-1, 1), Mino(1, 0)],
    Piece.L: [Mino(0, 0), Mino(-1, 0), Mino(1, 1), Mino(1, 0)],
}

PIECE_ICON_SHIFT = {
    Piece.I: Mino(-16, -8),
    Piece.O: Mino(-16, 0),
    Piece.T: Mino(-8, 0),
    Piece.S: Mino(-8, 0),
    Piece.Z: Mino(-8, 0),
    Piece.J: Mino(-8, 0),
    Piece.L: Mino(-8, 0)
}

# Rotation
def rotateShapeClockwise(shape: list[Mino]):
    shape[:] = [Mino(cell.y, -cell.x) for cell in shape]
def rotateShapeCounterclockwise(shape: list[Mino]):
    shape[:] = [Mino(-cell.y, cell.x) for cell in shape]
def rotateShape(shape: list[Mino], rotateCount: int):
    rotateCount %= 4
    if rotateCount == 1:
        rotateShapeClockwise(shape)
    elif rotateCount == 2:
        rotateShapeClockwise(shape)
        rotateShapeClockwise(shape)
    elif rotateCount == 3:
        rotateShapeCounterclockwise(shape)

SRS_KICKS = {
    Piece.I: [Offset([Mino(0, 0), Mino(-1, 0), Mino(2, 0), Mino(-1, 0), Mino(2, 0)]),
              Offset([Mino(-1, 0), Mino(0, 0), Mino(0, 0), Mino(0, 1), Mino(0, -2)]),
              Offset([Mino(-1, 1), Mino(1, 1), Mino(-2, 1), Mino(1, 0), Mino(-2, 0)]),
              Offset([Mino(0, 1), Mino(0, 1), Mino(0, 1), Mino(0, -1), Mino(0, 2)])],
    Piece.O: [Offset([Mino(0, 0)]),
              Offset([Mino(0, -1)]),
              Offset([Mino(-1, -1)]),
              Offset([Mino(-1, 0)])],
    Piece.T: [Offset([Mino(0, 0), Mino(0, 0), Mino(0, 0), Mino(0, 0), Mino(0, 0)]),
              Offset([Mino(0, 0), Mino(1, 0), Mino(1, -1), Mino(0, 2), Mino(1, 2)]),
              Offset([Mino(0, 0), Mino(0, 0), Mino(0, 0), Mino(0, 0), Mino(0, 0)]),
              Offset([Mino(0, 0), Mino(-1, 0), Mino(-1, -1), Mino(0, 2), Mino(-1, 2)])],
    Piece.S: [Offset([Mino(0, 0), Mino(0, 0), Mino(0, 0), Mino(0, 0), Mino(0, 0)]),
              Offset([Mino(0, 0), Mino(1, 0), Mino(1, -1), Mino(0, 2), Mino(1, 2)]),
              Offset([Mino(0, 0), Mino(0, 0), Mino(0, 0), Mino(0, 0), Mino(0, 0)]),
              Offset([Mino(0, 0), Mino(-1, 0), Mino(-1, -1), Mino(0, 2), Mino(-1, 2)])],
    Piece.Z: [Offset([Mino(0, 0), Mino(0, 0), Mino(0, 0), Mino(0, 0), Mino(0, 0)]),
              Offset([Mino(0, 0), Mino(1, 0), Mino(1, -1), Mino(0, 2), Mino(1, 2)]),
              Offset([Mino(0, 0), Mino(0, 0), Mino(0, 0), Mino(0, 0), Mino(0, 0)]),
              Offset([Mino(0, 0), Mino(-1, 0), Mino(-1, -1), Mino(0, 2), Mino(-1, 2)])],
    Piece.J: [Offset([Mino(0, 0), Mino(0, 0), Mino(0, 0), Mino(0, 0), Mino(0, 0)]),
              Offset([Mino(0, 0), Mino(1, 0), Mino(1, -1), Mino(0, 2), Mino(1, 2)]),
              Offset([Mino(0, 0), Mino(0, 0), Mino(0, 0), Mino(0, 0), Mino(0, 0)]),
              Offset([Mino(0, 0), Mino(-1, 0), Mino(-1, -1), Mino(0, 2), Mino(-1, 2)])],
    Piece.L: [Offset([Mino(0, 0), Mino(0, 0), Mino(0, 0), Mino(0, 0), Mino(0, 0)]),
              Offset([Mino(0, 0), Mino(1, 0), Mino(1, -1), Mino(0, 2), Mino(1, 2)]),
              Offset([Mino(0, 0), Mino(0, 0), Mino(0, 0), Mino(0, 0), Mino(0, 0)]),
              Offset([Mino(0, 0), Mino(-1, 0), Mino(-1, -1), Mino(0, 2), Mino(-1, 2)])],
}

SRS_180_KICKS = {
    Piece.I: [Offset([Mino(1, -1), Mino(1, 0)]),
              Offset([Mino(-1, -1), Mino(0, -1)]),
              Offset([Mino(-1, 1), Mino(-1, 0)]),
              Offset([Mino(1, 1), Mino(0, 1)])],
    Piece.O: [Offset([Mino(1, 1)]),
              Offset([Mino(1, -1)]),
              Offset([Mino(-1, -1)]),
              Offset([Mino(-1, 1)])],
    Piece.T: [Offset([Mino(0, 0), Mino(0, 1), Mino(1, 1), Mino(-1, 1), Mino(1, 0), Mino(-1, 0)]),
              Offset([Mino(0, 0), Mino(0, -1), Mino(-1, -1), Mino(1, -1), Mino(-1, 0), Mino(1, 0)]),
              Offset([Mino(0, 0), Mino(1, 0), Mino(1, 2), Mino(1, 1), Mino(0, 2), Mino(0, 1)]),
              Offset([Mino(0, 0), Mino(-1, 0), Mino(-1, 2), Mino(-1, 1), Mino(0, 2), Mino(0, 1)])],
    Piece.S: [Offset([Mino(0, 0), Mino(0, 1)]),
              Offset([Mino(0, 0), Mino(1, 0)]),
              Offset([Mino(0, 0), Mino(0, -1)]),
              Offset([Mino(0, 0), Mino(-1, 0)])],
    Piece.Z: [Offset([Mino(0, 0), Mino(0, 1)]),
              Offset([Mino(0, 0), Mino(1, 0)]),
              Offset([Mino(0, 0), Mino(0, -1)]),
              Offset([Mino(0, 0), Mino(-1, 0)])],
    Piece.J: [Offset([Mino(0, 0), Mino(0, 1), Mino(1, 1), Mino(-1, 1), Mino(1, 0), Mino(-1, 0)]),
              Offset([Mino(0, 0), Mino(0, -1), Mino(-1, -1), Mino(1, -1), Mino(-1, 0), Mino(1, 0)]),
              Offset([Mino(0, 0), Mino(1, 0), Mino(1, 2), Mino(1, 1), Mino(0, 2), Mino(0, 1)]),
              Offset([Mino(0, 0), Mino(-1, 0), Mino(-1, 2), Mino(-1, 1), Mino(0, 2), Mino(0, 1)])],
    Piece.L: [Offset([Mino(0, 0), Mino(0, 1), Mino(1, 1), Mino(-1, 1), Mino(1, 0), Mino(-1, 0)]),
              Offset([Mino(0, 0), Mino(0, -1), Mino(-1, -1), Mino(1, -1), Mino(-1, 0), Mino(1, 0)]),
              Offset([Mino(0, 0), Mino(1, 0), Mino(1, 2), Mino(1, 1), Mino(0, 2), Mino(0, 1)]),
              Offset([Mino(0, 0), Mino(-1, 0), Mino(-1, 2), Mino(-1, 1), Mino(0, 2), Mino(0, 1)])],
}

# endregion

# region Initialization

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode(SCREEN)
pygame.display.set_caption("Tetris")
gameIcon = pygame.image.load("icon.png")
pygame.display.set_icon(gameIcon)
clock = pygame.time.Clock()
running = True
FRAMERATE = data['Framerate']
dt = 0

BORDER_COLOR = (63, 63, 63)
LIMIT_COLOR = (255, 63, 63)

TOP_BUFFER = 20
bigText = pygame.font.SysFont("terminusttf", 50)
smallText = pygame.font.SysFont("terminusttf", 20)
holdText = bigText.render("HOLD", True, (255, 255, 255))
queueText = bigText.render("NEXT", True, (255, 255, 255))
spinType = ""
clearType = ""
allClear = ""
backToBack = -1

# endregion

# region Board

board: list[list[int]] = [[0] * boardHeight for _ in range(boardWidth)]

def clearBoard():
    board[:] = [[0]*boardHeight for _ in range(boardWidth)]

def drawBoard():
    screen.blit(holdText, ((SIDE_BUFFER-holdText.get_width())/2, TOP_BUFFER))
    screen.blit(queueText, (SIDE_BUFFER + BOARD_THICKNESS*2 + MINO_SIZE * boardWidth + (SIDE_BUFFER-queueText.get_width())/2, TOP_BUFFER))
    
    y = 170
    if backToBack > 0:
        b2bText = smallText.render(f'B2B x {backToBack}', True, (255, 255, 255))
        screen.blit(b2bText, ((SIDE_BUFFER - b2bText.get_width())/2, y))
        y += 35
    if len(spinType) != 0:
        spinText = smallText.render(spinType, True, (255, 255, 255))
        screen.blit(spinText, ((SIDE_BUFFER - spinText.get_width())/2, y))
        y += 35
    if len(clearType) != 0:
        clearText = smallText.render(clearType, True, (255, 255, 255))
        screen.blit(clearText, ((SIDE_BUFFER - clearText.get_width())/2, y))
        y += 35
    if len(allClear) != 0:
        allClearText = smallText.render(allClear, True, (255, 255, 255))
        screen.blit(allClearText, ((SIDE_BUFFER - allClearText.get_width())/2, y))
        y += 35

    pygame.draw.lines(screen, BORDER_COLOR, False, [(SIDE_BUFFER + BOARD_THICKNESS//2, BOARD_THICKNESS//2),
                                                    (SIDE_BUFFER + BOARD_THICKNESS//2, HEIGHT-BOARD_THICKNESS//2),
                                                    (SIDE_BUFFER + BOARD_THICKNESS + MINO_SIZE * boardWidth + BOARD_THICKNESS // 2, HEIGHT-BOARD_THICKNESS//2),
                                                    (SIDE_BUFFER + BOARD_THICKNESS + MINO_SIZE * boardWidth + BOARD_THICKNESS // 2, BOARD_THICKNESS//2)], width=BOARD_THICKNESS)
    for x in range(boardWidth):
        for y in range(boardHeight):
            pygame.draw.rect(screen, BORDER_COLOR, pygame.Rect(x*MINO_SIZE+(SIDE_BUFFER + BOARD_THICKNESS), (boardHeight-y-1)*MINO_SIZE, MINO_SIZE, MINO_SIZE))
    pygame.draw.rect(screen, LIMIT_COLOR, pygame.Rect(SIDE_BUFFER + BOARD_THICKNESS, (boardHeight-playingHeight)*MINO_SIZE-1, MINO_SIZE * boardWidth, 2))

def printBoard():
    for x in range(boardWidth):
        for y in range(boardHeight):
            color = (0, 0, 0)
            if board[x][y] >= 0:
                color = COLORS[board[x][y]]
            else:
                color = tuple(_//2 for _ in COLORS[-board[x][y]])
            pygame.draw.rect(screen, color, pygame.Rect(x*MINO_SIZE+(SIDE_BUFFER + BOARD_THICKNESS)+1, (boardHeight-y-1)*MINO_SIZE+1, MINO_SIZE-2, MINO_SIZE-2))
    return

# draws an icon in the middle of a rectangle shifted by (shiftX, shiftY)
def drawIcon(pieceID: Piece, length, width, shiftX, shiftY):
    cells = SHAPE[pieceID]
    for cell in cells:
        position = Mino(shiftX, shiftY) + Mino(length//2, width//2) + PIECE_ICON_SHIFT[pieceID] + Mino(cell.x, -cell.y) * (MINO_SIZE//2)
        
        pygame.draw.rect(screen, COLORS[pieceID], pygame.Rect(position.x, position.y, MINO_SIZE//2, MINO_SIZE//2))

def countClear() -> int:
    lineCount = 0
    for tmp in range(boardHeight):
        filled = True
        for _ in range(boardWidth):
            if board[_][tmp] == 0:
                filled = False
        if filled:
            lineCount += 1
    return lineCount

def lineClear():
    global board
    tmp = 0
    while tmp < boardHeight:
        filled = True
        for _ in range(boardWidth):
            if board[_][tmp] == 0:
                filled = False
        if filled:
            for _ in range(boardWidth):
                board[_].pop(tmp)
                board[_].append(0)
        else:
            tmp += 1

def checkAllClear() -> bool:
    for x in range(boardWidth):
        for y in range(boardHeight):
            if board[x][y] != 0:
                return False
    return True

# endregion

# region Tetromino

class Tetromino:
    def __init__(self, pieceID: Piece | int, rotation: int, position: Mino):
        self.ID = pieceID
        self.lastAction = None
        self.shape = [Mino(_.x, _.y) for _ in SHAPE[pieceID]]
        self.rotation = rotation
        rotateShape(self.shape, self.rotation)
        self.position = Mino(position.x, position.y)

    def drawCells(self, value: int | str, ghost: bool = False):
        for cell in self.shape:
            cellPosition = cell + self.position
            board[cellPosition.x][cellPosition.y] = value
            if ghost:
                board[cellPosition.x][cellPosition.y] *= -1

    def checkCollision(self) -> bool:
        for cell in self.shape:
            cellPosition = cell + self.position
            if cellPosition.x < 0 or cellPosition.x >= boardWidth:
                return True
            if cellPosition.y < 0 or cellPosition.y >= boardHeight:
                return True
            if board[cellPosition.x][cellPosition.y] > 0:
                return True
        return False

    def canMove(self, dx, dy) -> bool:
        self.position.x += dx
        self.position.y += dy
        result = self.checkCollision()
        self.position.x -= dx
        self.position.y -= dy
        return not result
    
    def get(self, pos: Mino) -> int:
        if pos.x < 0 or pos.x >= boardWidth: return 0
        if pos.y < 0 or pos.y >= boardHeight: return 0
        return board[pos.x][pos.y]

    def checkSpin(self) -> bool:
        if self.lastAction[0:4] != "Spin":
            return False
        
        if self.ID == Piece.T:
            cornerCount = 0
            if self.get(self.position + Mino(-1, 1)) > 0: cornerCount += 1
            if self.get(self.position + Mino(1, 1)) > 0: cornerCount += 1
            if self.get(self.position + Mino(1, -1)) > 0: cornerCount += 1
            if self.get(self.position + Mino(-1, -1)) > 0: cornerCount += 1

            if cornerCount >= 3:
                return True
        if self.canMove(-1, 0):
            return False
        if self.canMove(1, 0):
            return False
        if self.canMove(0, -1):
            return False
        if self.canMove(0, 1):
            return False
        return True
    
    def checkTspin(self) -> bool:
        if self.lastAction == "Spin+":
            return True
        
        corner = [0, 0, 0, 0]
        if self.get(self.position + Mino(-1, 1)) > 0: corner[0] = 1
        if self.get(self.position + Mino(1, 1)) > 0: corner[1] = 1
        if self.get(self.position + Mino(1, -1)) > 0: corner[2] = 1
        if self.get(self.position + Mino(-1, -1)) > 0: corner[3] = 1

        if corner[0] + corner[1] + corner[2] + corner[3] < 3:
            return False
        if corner[self.rotation] + corner[(self.rotation+1)%4] == 2:
            return True
        return False

    def lockPiece(self):
        global clearType, spinType, allClear, backToBack

        self.drawCells(self.ID)
        clearCount = countClear()

        spin = self.checkSpin()
        spinType = ""
        if spin:
            if self.ID != Piece.T:
                spinType = NAME[self.ID] + "-Spin mini"
            else:
                if self.checkTspin():
                    spinType = "T-spin"
                else:
                    spinType = "T-spin mini"
        
        if clearCount == 0:
            clearType = ""
            return

        if clearCount == 1: clearType = "Single"
        elif clearCount == 2: clearType = "Double"
        elif clearCount == 3: clearType = "Triple"
        elif clearCount == 4: clearType = "Quad"

        lineClear()
        if checkAllClear():
            allClear = "All Clear!"
            backToBack += 1
        else:
            allClear = ""
            if spin or clearCount == 4:
                backToBack += 1
            else:
                backToBack = -1

    def moveLeft(self):
        self.position.x -= 1
        if self.checkCollision():
            self.position.x += 1
        self.lastAction = "Left"

    def moveRight(self):
        self.position.x += 1
        if self.checkCollision():
            self.position.x -= 1
        self.lastAction = "Right"

    def moveDown(self) -> bool:
        self.position.y -= 1
        if self.checkCollision():
            self.position.y += 1
            return False
        self.lastAction = "Down"
        return True

    def hardDrop(self):
        while (True):
            if not self.moveDown():
                break

    def rotateClockwise(self):
        newRotation = (self.rotation+1)%4
        tests = SRS_KICKS[self.ID][self.rotation] - SRS_KICKS[self.ID][newRotation]

        rotateShape(self.shape, 1)
        for _ in range(len(tests)):
            self.position = self.position + tests[_]
            if not self.checkCollision():
                self.rotation = newRotation
                if self.ID == Piece.T and _ == 4:
                    self.lastAction = "Spin+"
                else:
                    self.lastAction = "Spin"
                return
            self.position = self.position - tests[_]
        rotateShape(self.shape, -1)

    def rotateCounterclockwise(self):
        newRotation = (self.rotation-1)%4
        tests = SRS_KICKS[self.ID][self.rotation] - SRS_KICKS[self.ID][newRotation]

        rotateShape(self.shape, -1)
        for _ in range(len(tests)):
            self.position = self.position + tests[_]
            if not self.checkCollision():
                self.rotation = newRotation
                if self.ID == Piece.T and _ == 4:
                    self.lastAction = "Spin+"
                else:
                    self.lastAction = "Spin"
                return
            self.position = self.position - tests[_]
        rotateShape(self.shape, 1)

    def rotate180(self):
        newRotation = (self.rotation+2)%4
        tests = SRS_180_KICKS[self.ID][self.rotation]

        rotateShape(self.shape, 2)
        for test in tests:
            self.position = self.position + test
            if not self.checkCollision():
                self.rotation = newRotation
                self.lastAction = "Spin"
                return
            self.position = self.position - test
        rotateShape(self.shape, -2)

# endregion

# region Piece management

holdPiece: Tetromino = None
currentPiece: Tetromino = None
ghostPiece: Tetromino = None
nextQueue: list[Tetromino] = []
bag: list[Tetromino] = []
def generatePiece() -> Tetromino:
    global bag
    if len(bag) == 0:
        bag = PIECE[:]
        random.shuffle(bag)
    chosen = bag.pop(0)
    return Tetromino(chosen, 0, SPAWN_POSITION)

def getPiece():
    global currentPiece, nextQueue
    currentPiece = nextQueue.pop(0)
    nextQueue.append(generatePiece())

    if currentPiece.checkCollision():
        global death
        death = True

def swapHold():
    global currentPiece, holdPiece
    holdPiece, currentPiece = currentPiece, holdPiece
    holdPiece = Tetromino(holdPiece.ID, 0, SPAWN_POSITION)
    if currentPiece == None:
        getPiece()

def resetGame():
    global holdPiece, ghostPiece, currentPiece, board, nextQueue, death, bag
    global spinType, clearType, allClear, backToBack
    death = False

    spinType = ""
    clearType = ""
    allClear = ""
    backToBack = -1

    bag = []
    nextQueue = []
    holdPiece = None
    ghostPiece = None
    currentPiece = None
    board = [[0] * boardHeight for _ in range(boardWidth)]
    while len(nextQueue) < PREVIEW_SIZE:
        nextQueue.append(generatePiece())
    getPiece()

# endregion

# region Input, Output

def outputBoard():
    screen.fill((0, 0, 0))

    if holdPiece != None:
        drawIcon(holdPiece.ID, SIDE_BUFFER, MINO_SIZE//2*3, 0, TOP_BUFFER*2 + holdText.get_height())
    for _ in range(PREVIEW_SIZE):
        drawIcon(nextQueue[_].ID, SIDE_BUFFER, MINO_SIZE//2*3, SIDE_BUFFER + BOARD_THICKNESS*2 + MINO_SIZE * boardWidth, TOP_BUFFER*2 + queueText.get_height() + MINO_SIZE//2*3*_)

    ghostPiece = Tetromino(currentPiece.ID, currentPiece.rotation, currentPiece.position)
    ghostPiece.hardDrop()
    ghostPiece.drawCells(-ghostPiece.ID)
    currentPiece.drawCells(currentPiece.ID)
    drawBoard()
    printBoard()
    currentPiece.drawCells(0)
    ghostPiece.drawCells(0)

# left right soft_drop cw ccw 180 hold hd reset
previousInput = []
currentInput = [0] * 9
def parseInput():
    global previousInput, currentInput
    previousInput = currentInput
    currentInput = [0] * 9
    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_LEFT]:
        currentInput[0] = 1
    if keys[pygame.K_RIGHT]:
        currentInput[1] = 1
    if keys[pygame.K_DOWN]:
        currentInput[2] = 1
    if keys[pygame.K_UP] or keys[pygame.K_x]:
        currentInput[3] = 1
    if keys[pygame.K_z]:
        currentInput[4] = 1
    if keys[pygame.K_a]:
        currentInput[5] = 1
    if keys[pygame.K_c]:
        currentInput[6] = 1
    if keys[pygame.K_SPACE]:
        currentInput[7] = 1
    if keys[pygame.K_r]:
        currentInput[8] = 1


def processInput():
    global currentPiece, DASdirection, DAShorizontal, DASdown
    if death:
        if currentInput[8] and not previousInput[8]:
            resetGame()
        return

    if currentInput[0] and not previousInput[0]:
        currentPiece.moveLeft()
        DAShorizontal = -DAS
        DASdirection = -1
    if not currentInput[0] and previousInput[0]:
        if currentInput[1] :
            DASdirection = 1
        else:
            DASdirection = -1
    
    if currentInput[1] and not previousInput[1]:
        currentPiece.moveRight()
        DAShorizontal = -DAS
        DASdirection = 1
    if not currentInput[1] and previousInput[1]:
        if currentInput[0] :
            DASdirection = -1
        else:
            DASdirection = 1

    if currentInput[2] and not previousInput[2]:
        currentPiece.moveDown()
        DASdown = -SDF
    
    processDAS()

    if currentInput[3] and not previousInput[3]:
        currentPiece.rotateClockwise()
    if currentInput[4] and not previousInput[4]:
        currentPiece.rotateCounterclockwise()
    if currentInput[5] and not previousInput[5]:
        currentPiece.rotate180()
    if currentInput[6] and not previousInput[6]:
        swapHold()
    if currentInput[7] and not previousInput[7]:
        currentPiece.hardDrop()
        currentPiece.lockPiece()
        getPiece()
    if currentInput[8] and not previousInput[8]:
        resetGame()

def processDAS():
    global DAShorizontal, DASdirection, DASdown, currentPiece

    downCount = 0
    horizontalCount = 0
    if currentInput[2]: DASdown += dt
    if currentInput[0] or currentInput[1]: DAShorizontal += dt

    if ARR == 0:
        if DAShorizontal >= 0 and (currentInput[0] or currentInput[1]):
            horizontalCount = 100
            DAShorizontal = -1
    else:
        if DAShorizontal >= 0:
            horizontalCount = DAShorizontal // ARR + 1
            DAShorizontal -= horizontalCount * ARR
    
    if SDF == 0:
        if DASdown >= 0 and currentInput[2]:
            downCount = 100
            DASdown = -1
    else:
        if DASdown >= 0:
            downCount = DASdown // SDF + 1
            DASdown -= downCount * SDF
    
    while True:
        previousPosition = Mino(currentPiece.position.x, currentPiece.position.y)

        # move sideways
        if horizontalCount > 0:
            if DASdirection == -1:
                currentPiece.position.x -= 1
                if not currentPiece.checkCollision():
                    horizontalCount -= 1
                    currentPiece.lastAction = "Left"
                else:
                    currentPiece.position.x += 1
            else:
                currentPiece.position.x += 1
                if not currentPiece.checkCollision():
                    horizontalCount -= 1
                    currentPiece.lastAction = "Right"
                else:
                    currentPiece.position.x -= 1

        # move down
        while downCount > 0:
            currentPiece.position.y -= 1
            if currentPiece.checkCollision():
                currentPiece.position.y += 1
                break
            downCount -= 1
            currentPiece.lastAction = "Down"

        currentPosition = Mino(currentPiece.position.x, currentPiece.position.y)
        if previousPosition == currentPosition:
            break

# endregion

# region Main
resetGame()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    parseInput()
    processInput()

    outputBoard()
    pygame.display.flip()
    dt = clock.tick(FRAMERATE)


pygame.quit()

# endregion