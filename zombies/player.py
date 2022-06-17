import pygame 
import os

class Player:

    def __init__(self, width, height, radius):
        self.radius = radius
        self.coordinates = [width/2 ,height/2]
        self.squares = []
        self.hits = 0
        self.texture = pygame.image.load(os.path.join('zombies/img', "lex.png"))
        self.texture = pygame.transform.scale(self.texture, (self.radius*2, self.radius*2))

    def move(self,x,y):
        self.coordinates = [x,y]

    def draw(self, win, texture):
        if(texture):
            rect = pygame.Rect(self.coordinates[0]-(self.radius), self.coordinates[1]-(self.radius), 10, 10)
            win.blit(self.texture, rect)
        else:
            pygame.draw.circle(win, (0, 255, 0), (self.coordinates[0], self.coordinates[1]), self.radius)