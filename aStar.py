import random

class Node:
    def __init__(self, coord, g, h, move, parent):
        self.coordinates = coord
        self.g = g
        self.h = h
        self.move = move
        self.parent = parent

class aStarAlg:
    def __init__(self):
        self.targets = [[50,50],[950,50],[950,650],[50,650]]
        self.currentTarget = random.choice([0, 1, 2, 3])
        self.openList = []
        self.closedList = []

    def runAStar(self, gameboard, player):
        if(player == self.targets[self.currentTarget]):
            self.getNextTarget()

        self.openList = []
        self.closedList = []

        node = Node(player, 0, self.getDistance(player, self.targets[self.currentTarget]), 1, 0)
        self.openList.append(node)
        
        while True:
            if(len(self.openList) == 0):
                return random.choice([0, 1, 2, 3])

            currentNode = self.getLowestF()
            self.openList.remove(currentNode)
            self.closedList.append(currentNode)

            #Is it the end goal?
            if(int(currentNode.coordinates[0]) == self.targets[self.currentTarget][0] and int(currentNode.coordinates[1]) == self.targets[self.currentTarget][1]):
                self.openList = []
                self.closedList = []
                firstMove = self.getFirstMove(currentNode)
                return firstMove.move

            self.Evaluate(currentNode, gameboard)

    def getFirstMove(self, currentNode):
        while(currentNode.parent.parent != 0):
            currentNode = currentNode.parent
        return currentNode 

    def getLowestF(self):
        lowest = self.openList[0]
        for node in self.openList:
            if(node.h + node.g < lowest.h + lowest.g):
                lowest = node
        return lowest

    def getNextTarget(self):
        if(self.currentTarget == 0):
            self.currentTarget = 1
        elif(self.currentTarget == 1):
            self.currentTarget = 2
        elif(self.currentTarget == 2):
            self.currentTarget = 3
        elif(self.currentTarget == 3):
            self.currentTarget = 0

    def Evaluate(self, node, gameboard):
        #         Up       Down    Left     Right
        moves = [[0,-10], [0,10], [-10,0], [10,0]]

        for i in range(len(moves)):
            move = moves[i]
            newCoordinates = [node.coordinates[0] + move[0], node.coordinates[1] + move[1]]
            if(self.isValidMove(newCoordinates, gameboard) and not self.isInClosedList(newCoordinates)):
                newNode = Node(newCoordinates, node.g + 1, self.getDistance(newCoordinates, self.targets[self.currentTarget]), i+1, node)
                if(not self.inOpenList(newNode)):
                    self.openList.append(newNode)

    def isValidMove(self, coordinates, gameboard):
        moves = [[0,-10], [-10,-10], [10,10], [0,10], [-10,0], [-10,10], [10,0], [10,-10]]
        for i in range(len(moves)):
            move = moves[i]
            newCoordinates = [coordinates[0] + move[0], coordinates[1] + move[1]]
            if(int(newCoordinates[0]/10) > 101 or int(newCoordinates[1]/10) > 71):
                return False
            if(gameboard[int(newCoordinates[0]/10)][int(newCoordinates[1]/10)] != 0 and gameboard[int(newCoordinates[0]/10)][int(newCoordinates[1]/10)] != 1):
                return False
        return True

    def getDistance(self, newNode, target):
        a = target[0] - newNode[0]
        b = target[1] - newNode[1]
        return (a * a) + (b * b)

    def isInClosedList(self, newCoordinates):
        for node in self.closedList:
            if(node.coordinates == newCoordinates):
                return True
        return False

    def inOpenList(self, newNode):
        for node in self.openList:
            if(node.coordinates[0] == newNode.coordinates[0] and node.coordinates[1] == newNode.coordinates[1]):
                if(newNode.g < node.g):
                    node.parent = newNode.parent
                    node.g = newNode.g
                    node.h = newNode.h
                return True
        return False