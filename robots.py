import numpy as np
import random
import time

DEBUG0 = True
DEBUG1 = False

class Board:
    DECREASEP = 0
    DECREASEA = 1
    MAXANTS = 150
    MAXPHEROMONE = 1
    TICK = 0
    allMail = 0
    
    def __init__(self, filename):
        file = open(filename)
        lines = file.readlines()
        self.y = int(lines[0].split()[0])
        self.x = int(lines[0].split()[1])
        self.data = []
        self.box = list(map(int, lines[1].split()))
        self.spawns = []
        for line in lines[2:]:
            self.data.append([])
            for cell in line.split():
                self.data[-1].append(cell)
                if self.data[-1][-1] == '0':
                    self.data[-1][-1] = 0
                if isinstance(self[len(self.data)-1][len(self.data[-1])-1], str) and self[len(self.data)-1][len(self.data[-1])-1][0] == 'S':
                    self.spawns.append(Spawnpoint(len(self.data)-1, len(self.data[-1])-1, self))
        self.mail = []
        self.ants = []
        self.antmap = [[0 for i in range(self.x)] for j in range(self.y)]
        file.close()
    
    def loadMail(self, filename):
        file = open(filename)
        data = file.readlines()[0]
        for i in data.split():
            self.allMail += 1
            self.mail.append(int(i))
        file.close()
    
    def consolePrint(self):
        for i in self.data:
            for j in i:
                print(' '*(3-len(str(j))) + str(j), end=' ')
            print()
            
    def __str__(self):
        ans = ''
        for i in self.data:
            for j in i:
                ans += ' '*(3-len(str(j))) + str(j) + ' '
            ans += '\n'
        return ans[:-1]
            
    def tick(self, decreasing = True):
        if DEBUG0 or DEBUG1:
            print(f"TICK {self.TICK}")
        self.TICK += 1
        if DEBUG1:
            print("Calculating MAXPHEROMONE")
            
        self.MAXPHEROMONE= 1
        for i in range(len(self.data)):
            for j in range(len(self.data[i])):
                if isinstance(self[i][j], float) or isinstance(self[i][j], int):
                    if (self[i][j] > self.MAXPHEROMONE):
                        self.MAXPHEROMONE = self[i][j]
        if DEBUG0 or DEBUG1:
            print(f'Ants: {len(self.ants)}, maxPheromone: {"%.2f" % self.MAXPHEROMONE}, task: {self.allMail - len(self.mail) - len(self.ants)}/{self.allMail}')
        if DEBUG1:
            print("Processing SPAWNS")
        for spawnpoint in self.spawns:
            spawnpoint.process()
        if DEBUG1:
            print("Processing ANTS: ", end='')
            print(*[i.ID for i in self.ants], sep = ' | ')
        for ant in self.ants:
            ant.process()
        if decreasing:
            self.decrease()
            
    def decrease(self):
        for i in range(len(self.data)):
            for j in range(len(self.data[i])):
                if isinstance(self[i][j], float) or isinstance(self[i][j], int):
                    self[i][j] = max(0, self[i][j] - self.DECREASEA)
                    self[i][j] *= 1-self.DECREASEP/100
                    
    def validNeibours(self, y, x):
        neighbours = [(y+1, x), (y-1, x), (y, x+1), (y, x-1)]
        ans = []
        for i in range(len(neighbours)):
            if 0 <= neighbours[i][0] < self.y and 0 <= neighbours[i][1] < self.x and (isinstance(self[neighbours[i][0]][neighbours[i][1]], float) or isinstance(self[neighbours[i][0]][neighbours[i][1]], int)):
                if self.antmap[neighbours[i][0]][neighbours[i][1]] == 0:
                    ans.append(neighbours[i])
        return ans

    def checkBox(self, y, x, load):
        neighbours = [(y+1, x), (y-1, x), (y, x+1), (y, x-1)]
        ans = []
        for i in range(len(neighbours)):
            if 0 <= neighbours[i][0] < self.y and 0 <= neighbours[i][1] < self.x and isinstance(self[neighbours[i][0]][neighbours[i][1]], str) and self[neighbours[i][0]][neighbours[i][1]][0] == 'B':
                if (self.box[int(self[neighbours[i][0]][neighbours[i][1]][1:])-1] == load):
                    return True
        return False
    
    def getLoad(self):
        return self.mail.pop(0)
                
    def __getitem__(self, k):
        if isinstance(k, int):
            if k < -self.y or k >= self.y:
                raise IndexError("Index of bounds")
            k =  k + self.y if k < 0 else k
            return self.data[k]
        raise TypeError("Index must be int")     
        
class Spawnpoint:
    def __init__(self, y, x, board):
        self.x = x
        self.y = y
        self.board = board
        
    def process(self):
        if DEBUG1:
            print(f"Process SPAWN {self.y}, {self.x}")
        if self.isfree() and len(self.board.mail) > 0:
            self.createAnt(self.y, self.x)
            
    def isfree(self):
        if self.board.antmap[self.y][self.x] == 0:
            return True
        return False
    
    def createAnt(self, y, x):
        if len(self.board.ants) < self.board.MAXANTS:
            self.board.ants.append(Ant(y, x, self.board, self.board.getLoad()))
            self.board.antmap[y][x] = 1

class Ant:
    _counter = 0   
    FERPERRUN = 3000
    BASEPROB = 10
    
    def __init__(self, y, x, board, load):
        Ant._counter += 1
        self.x = x
        self.y = y
        self.board = board
        self.load = load
        self.ID = Ant._counter
        self.path = []
        
    def __str__(self):
        return f'id:{self.ID}, load:{self.load}, i:{self.y}, j:{self.x}'    
    
    def process(self):
        if DEBUG1:
            print(f"Process ANT {self.ID}: {self.y}, {self.x}")
        if self.board.checkBox(self.y, self.x, self.load):
            self.leavePheromone()
            self.board.antmap[self.y][self.x] = 0
            self.board.ants.remove(self)
            return
        neighbours = self.board.validNeibours(self.y, self.x)
        if len(neighbours) == 0:
            return
        weights = [10+self.board[neighbour[0]][neighbour[1]] for neighbour in neighbours]
        decicion = random.random()*sum(weights)
        ind = 0
        while decicion > sum(weights[0:ind+1]):
            ind += 1
        self.path.append((neighbours[ind][0], neighbours[ind][1]))
        self.board.antmap[self.y][self.x] = 0
        self.y, self.x = neighbours[ind][0], neighbours[ind][1]
        self.board.antmap[self.y][self.x] = 1
        
    def leavePheromone(self):
        for i in self.path:
            self.board[i[0]][i[1]] += self.FERPERRUN/len(self.path)

board = Board('map.txt')
board.loadMail('mail.txt')

MODE = 0
if MODE == 0:
    import pygame
    import matplotlib as mpl
    import matplotlib.pyplot as plt    
    
    def colorFader(c1='#7109aa',c2='#FFFF00',mix=0): #fade (linear interpolate) from color c1 (at mix=0) to c2 (mix=1)
        mix = min(max(0, mix), 1)
        c1=np.array(mpl.colors.to_rgb(c1))
        c2=np.array(mpl.colors.to_rgb(c2))
        return mpl.colors.to_hex((1-mix)*c1 + mix*c2)
    
    TILE = 25
    
    RES = WIDTH, HEIGHT = TILE*board.x, TILE*board.y
    FPS = 20
    
    pygame.init()
    surface = pygame.display.set_mode(RES)
    clock = pygame.time.Clock()
    
    font = pygame.font.Font(None, 30)
    fontsmall = pygame.font.Font(None, 15)
    
    if (DEBUG1):
        print(board.y, board.x)
    
    while True:
        flag = False
        if len(board.ants) <= 0 and board.TICK > 0:
            flag = True        
        
        surface.fill(pygame.Color('black'))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                break
        
        for i in range(board.y):
            for j in range(board.x):
                if (DEBUG1):
                    print(i, j, end=' ')
                if isinstance(board[i][j], float) or isinstance(board[i][j], int):
                    color = colorFader(mix=(board[i][j]+Ant.BASEPROB)/(board.MAXPHEROMONE + Ant.BASEPROB))
                    pygame.draw.rect(surface, color, (j*TILE + 2, i*TILE + 2, TILE - 2, TILE - 2))
                    if (DEBUG1):
                        print('PATH')
                elif (board[i][j][0] == 'B'):
                    color = '#00FF00'
                    pygame.draw.rect(surface, color, (j*TILE + 2, i*TILE + 2, TILE - 2, TILE - 2))
                    text = font.render(str(board.box[int(board[i][j][1:])-1]), True, 'black')
                    surface.blit(text, [j*TILE + int(TILE/2) - 6, i*TILE + int(TILE/2) - 6] ) 
                    if (DEBUG1):
                        print('BOX')
                elif (board[i][j] == 'x'):
                    color = '#000000'
                    pygame.draw.rect(surface, color, (j*TILE + 2, i*TILE + 2, TILE - 2, TILE - 2))
                    pygame.draw.line(surface, pygame.Color('red'), (j*TILE, i*TILE), ((j+1)*TILE, (i+1)*TILE), 3)
                    pygame.draw.line(surface, pygame.Color('red'), ((j+1)*TILE, i*TILE), (j*TILE, (i+1)*TILE), 3)
                    if (DEBUG1):
                        print('WALL')
                elif (board[i][j] == 'S'):
                    color = '#FFFFFF'
                    pygame.draw.rect(surface, color, (j*TILE + 2, i*TILE + 2, TILE - 2, TILE - 2))
                    text = font.render("S", True, 'black')
                    surface.blit(text, [j*TILE + int(TILE/2) - 6, i*TILE + int(TILE/2) - 6] )
                    if (DEBUG1):
                        print('SPAWN')
                if board.antmap[i][j] == 1:
                    pygame.draw.rect(surface, 'red', (j*TILE + TILE/2-4, i*TILE + TILE/2-4, 10, 10))
                    if (DEBUG1):
                        print('ANT')
        
        for ant in board.ants:
            text = fontsmall.render(str(ant.load), True, 'dimgray')
            surface.blit(text, [ant.x*TILE + int(TILE/2), ant.y*TILE + int(TILE/2) - 2] )             
        
        [pygame.draw.line(surface, pygame.Color('dimgray'), (x, 0), (x, HEIGHT)) for x in range(0, WIDTH, TILE)]
        [pygame.draw.line(surface, pygame.Color('dimgray'), (0, y), (WIDTH, y)) for y in range(0, HEIGHT, TILE)]
        
        board.tick()
        
        pygame.display.flip()
        time.sleep(1/FPS)
        
        if flag:
            break
        
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                break        
elif MODE == 1:
    while True:        
        board.tick() 
        time.sleep(1)
else:
    pass