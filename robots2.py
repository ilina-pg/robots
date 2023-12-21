import copy
import random

BASEPROB = 5
DECREASEP = 25
DECREASEA = 5
FERPERRUN = 100
TICK = 0

class Edge:
    
    def __init__(self, finish, weight, length=1):
        self.f = finish
        self.weight = copy.deepcopy(weight)
        self.length = length
        
    def decreace(self, percent=DECREASEP, absolute=DECREASEA):
        for i in range(len(self.weight)):
            self.weight[i] = max(0, elf.weight[i] - self.absolute)
            elf.weight[i] *= 1-self.percent/100        
    
    def __str__(self):
        return f'{self.f}'

class Vertex:
    
    def __init__(self, num, sort, free=True):
        self.sort = sort
        self.num = num
        self.free = free
        self.neighbours = []
        
    def addNeighbour(self, neighbour):
        self.neighbours.append(neighbour)
        
    def take(self):
        if self.free:
            self.free = False
            return True
        return False
        
    def liberate(self):
        if not self.free:
            self.free = True
            return True
        return False

class Graph:
    size = None
    
    def __init__(self, N):
        self.N = N
        self.graph = [Vertex(i, 0) for i in range(N)]
        
    def addEdge(self, start, finish, weight, length=1):
        if (self.size is None):
            self.size = len(weight)
        elif self.size != len(weight):
            print('Некорректный размер массива весов')
            return
        self[start].addNeighbour(Edge(finish, weight, length))
        
    def decrease(self, percent=DECREASEP, absolute=DECREASEA):
        for v in self.graph:
            for e in v.neighbours:
                e.decrease()
        
    def __getitem__(self, k):
        if isinstance(k, int):
            if not (0 <= k < self.N):
                raise IndexError("Index of bounds")
            return self.graph[k]
        raise TypeError("Index must be int")      
        
    def __str__(self):
        ans = ''
        for v in self.graph:
            ans += f'{v.num} ({"free" if v.free else "taken"}): '
            for n in v.neighbours:
                ans += f'({n.f} {str(n.weight)}) '
            ans += '\n'
        return ans[:-1]
       
class Ant:
    
    def __init__(self, graph, pos, mode):
        self.graph = graph
        self.pos = pos
        self.mode = mode
        self.path = []
        self.graph[self.pos].take()
        
    def process(self):
        if self.mode and self.checkPoint():
            self.leaveFeromon()
            self.mode = 0
        if self.mode == 0 and self.checkLoad():
            self.leaveFeromon()
            self.mode = getLoad()
        neighbours = []
        for i in self.graph[self.pos].neighbours:
            if (self.graph[i.f].free):
                neighbours.append(i)
        if not len(neighbours):
            #print('Нет свободных путей')
            return
        weights = [neighbour.weight[self.mode] + BASEPROB for neighbour in neighbours]
        decicion = random.random()*sum(weights)
        ind = 0
        while decicion > sum(weights[0:ind+1]):
            ind += 1
        #print(f'Вершина {self.pos}, посылка {self.mode}')
        #print(*[neighbour.f for neighbour in neighbours])
        #print(weights)
        self.path.append(neighbours[ind])
        self.graph[self.pos].liberate()
        self.graph[neighbours[ind].f].take()
        self.pos = neighbours[ind].f
        print('k ',(self.pos, self.mode))
        return (self.pos, self.mode)
    
    def checkPoint(self):
        if self.graph[self.pos].sort == f'B{int(self.mode)}':
            return True
        for neighbour in self.graph[self.pos].neighbours:
            if self.graph[neighbour.f].sort == f'B{int(self.mode)}':
                return True
        return False
    
    def checkLoad(self):
        if self.graph[self.pos].sort == f'S':
            return True
        for neighbour in self.graph[self.pos].neighbours:
            if self.graph[neighbour.f].sort == f'S':
                return True
        return False
    
    def leaveFeromon(self):
        for v in self.path:
            v.weight[self.mode] += FERPERRUN/len(self.path)
        
class Board:
    
    def __init__(self, filename):
        file = open(filename)
        lines = file.readlines()
        self.y = int(lines[0].split()[0])
        self.x = int(lines[0].split()[1])
        self.box = list(map(int, lines[1].split()))
        self.graph = Graph(self.x*self.y)
        self.data = []
        self.ants = []
        
        for i in range(len(lines[2:])):
            self.data.append([])
            line = lines[2:][i].split()
            for j in range(len(line)):
                if (line[j] == 'R'):
                    line[j] = '0'
                    self.ants.append(Ant(self.graph, i*self.x+j, 0))
                self.data[-1].append(line[j])
                self.graph[i*self.x+j].sort = line[j]
                
                
        for i in range(self.y):
            for j in range(self.x):
                for nei in self.validNeighbours(i, j):
                    self.graph.addEdge(i*self.x+j, nei[0]*self.x + nei[1], [0 for k in range(max(self.box)+1)])
        
        file.close()
    
    def validNeighbours(self, i, j):
        neighbours = [(i+1, j), (i-1, j), (i, j+1), (i, j-1)]
        ans = []
        for i in range(len(neighbours)):
            if 0 <= neighbours[i][0] < self.y and 0 <= neighbours[i][1] < self.x and self.data[neighbours[i][0]][neighbours[i][1]] != 'x':
                ans.append(neighbours[i])
        return ans
    
    def __getitem__(self, k):
        if isinstance(k, int):
            if k < -self.y or k >= self.y:
                raise IndexError("Index of bounds")
            k =  k + self.y if k < 0 else k
            return self.data[k]
        raise TypeError("Index must be int")    
    
    def tick(self):
        log_str = ''
        for ant in self.ants:
            pos, mail = ant.process()
            log_str += f'robot in {pos // self.x} {pos % self.x} mail {mail}\n'
        return log_str
            
    def isEmpty(self):
        for ant in self.ants:
            if (ant.mode != 0):
                return False
        return True

def getLoad():
    return mail.pop(0)

file = open('mailA.txt')
mail = list(map(int, file.readlines()[0].split()))
file.close()

board = Board('mapA.txt')
file = open('log.txt', 'w')
while len(mail) or not board.isEmpty():
    TICK += 1
    print(len(mail))
    file.write(f'Iter {TICK}: \n' + board.tick() + '\n')
file.close()