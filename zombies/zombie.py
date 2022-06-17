import random
import pygame
import os

class Zombie:
    
    def __init__(self, time, player, width, height, radius, space_size, gameboard, initial):
        #Randomly generate coordinates 
        player_x, player_y = player
        x = random.randint(1,width/space_size)*space_size
        y = random.randint(1,height/space_size)*space_size

        #Making Zombies spawn near AI
        def inInnerBound(x,y):
            if((y<(player_y + 200) and y>(player_y - 200)) and (x<(player_x + 200) and x>(player_x - 200))):
                return True
            return False

        def inOuterBounds(x,y):
            if(x > player_x + 200 or x < player_x - 200):
                return True
            if(y > player_y + 200 or y < player_y - 200):
                return True
            return False

        def spotOpen(x,y,board):
            if(board[x][y] == 0):
                return True
            return False

        if(initial):
            while((inInnerBound(x,y) or inOuterBounds(x,y)) and spotOpen(int(x/space_size),int(y/space_size),gameboard)):
                x = random.randint(1,width/space_size)*space_size
                y = random.randint(1,height/space_size)*space_size
        else:
            while(((x>(player_x + 200) and x<(player_x - 200)) and (y<player_y + 200 or y>player_y - 200)) and spotOpen(int(x/space_size),int(y/space_size),gameboard)):
                x = random.randint(1,width/space_size)*space_size
                y = random.randint(1,height/space_size)*space_size

        self.coordinates = [x,y]
        self.timeBorn = time
        self.ttl = random.randint(0,200) + 100
        self.radius = radius

        self.texture = pygame.image.load(os.path.join('zombies/img', "zombie.png"))
        self.texture = pygame.transform.scale(self.texture, (self.radius*2, self.radius*2))

    def draw(self, win, texture):
        if(texture):
            rect = pygame.Rect(self.coordinates[0]-(self.radius), self.coordinates[1]-(self.radius), 10, 10)
            win.blit(self.texture, rect)
        else:
            pygame.draw.circle(win, (255, 0, 0), (self.coordinates[0], self.coordinates[1]), self.radius)
