import os
import time
import sys
import heapq
import curses

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class PriorityQueue:
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0
    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]


class Maze(object):
    def __init__(self, filename, costs = {'m': 3, 'p' : 2, '-' : 1, '#' : 100, 'b' : 10, '*' : 15}):
        self.filename =  filename
        self.costs = costs
        self.board = []
        self.width = []
        self.height = []
        self.nodes = {}
        self.graph = {}
        self.path = []
        self.screen = None
        self.enemy_pos = []
        maze = self.readFile()
        self.printBoard(maze)
        self.convertToGraph(maze)
        self.start,self.goal = self.findGoalAndStart()
        #self.a_star(start,goal)
        self.runGame()
        #self.printScreen()
        #self.updateScreen()

    def readFile(self):
        f = open(self.filename,'r')
        maze = []
        for line in f:
            maze.append(line.rstrip('\n'))
        self.height = len(maze)
        self.width = len(maze[0])
        return maze

    def findGoalAndStart(self):
        start = None
        goal = None
	for n in self.nodes:
            if self.nodes[n] == 'm':
                start = n
            if self.nodes[n] == 'p':
                goal = n
            if self.nodes[n] == 'b':
                self.enemy_pos.append(n)
        return (start,goal)


    def convertToGraph(self,maze):
        for i in range(0,self.height):
            for j in range(0,self.width):
                vertices = self.findNeighbors((j,i))
                self.graph[(j,i)] = vertices
                self.nodes[(j,i)] = maze[i][j]

    def printBoard(self,obj):
        for i in range(0,self.height):
            for j in range(0,self.width):
                print obj[i][j],
            print ''

    def cost(self, a, b):
        return self.costs[self.nodes[a]] + self.costs[self.nodes[b]]

    def heuristic(self,a,b):
        (x1, y1) = a
        (x2, y2) = b
        return abs(x1 - x2) + abs(y1 - y2)

    def a_star(self, start, goal):
        frontier = PriorityQueue()
        frontier.put(start, 0)
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0
        while not frontier.empty():
            current = frontier.get()
            if current == goal:
                break
            neighbors  = self.graph[current]
            for neighbor in neighbors:
                new_cost = cost_so_far[current] + self.cost(current,neighbor)
                if neighbor not in cost_so_far or new_cost  < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    priority = new_cost + self.heuristic(neighbor,goal)
                    frontier.put(neighbor,priority)
                    came_from[neighbor] = current


        path = self.reconstruct_path(came_from,start,goal)
        return path
        #self.printPath(self.path,'$')

    def reconstruct_path(self,came_from, start, goal):
        current = goal
        path = []
        while current != start:
            path.append(current)
            current = came_from[current]
        path.append(start) # optional
        path.reverse() # optional
        return path

    def printPath(self,path,char):
        x = sorted(self.nodes.keys(), key=lambda k: [k[1],k[0]])
        count = 0
        for n in x:
            if n in path:
                print bcolors.OKGREEN + char + bcolors.ENDC,
                count = count +1
            if n not in path:
                print self.nodes[n],
                count = count +1
            if count == self.width:
                print ''
                count = 0


    def findNeighbors(self,tile):
        x,y = (tile)
        UP = (x, y - 1)
        DOWN = (x, y + 1)
        LEFT = (x - 1,y)
        RIGHT = (x + 1, y)
        ulu = (x-1, y-1)
        uld = (x-1, y+1)
        uru = (x+1, y-1)
        urd = (x+1, y+1)
        directions = [UP,DOWN,LEFT,RIGHT, ulu,uld,uru,urd]
        neighbors = []
        for direc in directions:
            if direc[0] >= 0  and direc[0] < self.width and direc[1] >= 0 and direc[1] < self.height:
                neighbors.append(direc)
        return neighbors

    def printScreen(self,path,char):
        self.screen = curses.initscr()
        self.screen.clear()
        self.screen.border(0)
        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
        for y in range(0, self.height):
            for x in range(0,self.width):
                try:
                    if (x,y) ==  path:
                        self.screen.addstr(y,x,char,curses.A_BLINK)
                        self.start = (x,y)
                    else:
                        self.screen.addstr(y,x,self.nodes[(x,y)],curses.color_pair(1))
                    self.screen.refresh()
                    #screen.getch()
                except curses.error:
                    pass
            #screen.addstr('\n')
        time.sleep(1)
        #curses.endwin()

    def updateScreen(self,n_path):
        player = False
        for p in n_path:
            if player == False:
                self.printScreen(p,'m')
                player = True
            else:
                self.printScreen(p,'b')

        curses.endwin()

    def runGame(self):
        while self.start != self.goal:
            p_path = self.a_star(self.start,self.goal)
            u_path = []
            e_path = []
            for enemy in self.enemy_pos:
                e_path.append(self.a_star(enemy, self.start))
            #print p_path
            #u_path.append(p_path[1])
            self.nodes[p_path[0]] = '-'
            self.updateScreen(p_path[1])
            for e in e_path:
                self.nodes[e[0]] = "-"
                #print e[1]
                #u_path.append(e[1])
                self.updateScreen(e[1])

if __name__ == "__main__":
    Maze('maze_complex.txt')
    #Maze('simple_maze.txt')
