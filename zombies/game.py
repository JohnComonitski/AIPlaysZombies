from logging import NullHandler
import pygame
import random
from .player import Player
from .zombie import Zombie
pygame.init()

class GameInformation:
    def __init__(self, score, available_moves):
        self.score = score
        self.available_moves = available_moves

class Game:
    #Window Stats
    SCORE_FONT = pygame.font.SysFont("arial", 50)
    GAME_WIDTH = 1000
    GAME_HEIGHT = 700
    RADIUS = 10
    SPACE_SIZE = 10

    #Editable Game Stats
    TOTAL_ZOMBIES = 10
    ZOMBIE_SPEED = 3
    KILL_ZOMBIES = True

    def __init__(self, window, genome_stats):
        self.window = window
        self.genome_stats = genome_stats
        self.width = int(self.GAME_WIDTH/self.SPACE_SIZE)
        self.height = int(self.GAME_HEIGHT/self.SPACE_SIZE)
        self.gameboard = [[0]*(self.height + 2) for i in range((self.width + 2))] 
        self.score = 0
        self.direction = 2

        #Set player
        self.player = Player(self.GAME_WIDTH, self.GAME_HEIGHT, self.RADIUS)
        self.gameboard[int(self.player.coordinates[0]/self.SPACE_SIZE)][int(self.player.coordinates[1]/self.SPACE_SIZE)] = 1
        #Set Zombies
        zombies = []
        for i in range(self.TOTAL_ZOMBIES):
            zombie = Zombie(0, self.player.coordinates, self.GAME_WIDTH, self.GAME_HEIGHT, self.RADIUS, self.SPACE_SIZE, self.gameboard, True)
            zombies.append(zombie)
            self.gameboard[int(zombie.coordinates[0]/self.SPACE_SIZE)][int(zombie.coordinates[1]/self.SPACE_SIZE)] = 2

        self.zombies = zombies 

    def draw_score(self):
        score_text = self.SCORE_FONT.render(f"{self.score}", 1, (255,0,0))
        self.window.blit(score_text, (self.GAME_WIDTH // 2 - score_text.get_width()//2, 10))

    def draw_stats(self):
        if(self.genome_stats["gen"] != ''):
            val = self.genome_stats["gen"]
            score_text = self.SCORE_FONT.render(f"Generation: {val}", 1, (255,255,255))
            self.window.blit(score_text, (10, 10))

            val = self.genome_stats["Genome ID"]
            score_text = self.SCORE_FONT.render(f"Genome ID: {val}", 1, (255,255,255))
            self.window.blit(score_text, (10, 60))

            val = self.genome_stats["test"]
            score_text = self.SCORE_FONT.render(f"Test #{val}", 1, (255,255,255))
            self.window.blit(score_text, (10, 110))

            val = self.genome_stats["fitness"]
            score_text = self.SCORE_FONT.render(f"Total Fitness {val}", 1, (255,255,255))
            self.window.blit(score_text, (10, 160))

    def draw(self, draw_score=True, draw_textures=False, print_stats=True):
        self.window.fill((0,0,0))

        if draw_score:
            self.draw_score()

        if print_stats:
            self.draw_stats()

        for zombie in self.zombies:
            zombie.draw(self.window, draw_textures)

        self.player.draw(self.window, draw_textures)

    def kill_zombies(self):
        zombiesKilled = 0
        for zombie in self.zombies:
            if(zombie.timeBorn + zombie.ttl < self.score):
                zombiesKilled += 1
                self.gameboard[int(zombie.coordinates[0]/self.SPACE_SIZE)][int(zombie.coordinates[1]/self.SPACE_SIZE)] = 0
                self.zombies.remove(zombie)
                del zombie

        for i in range(zombiesKilled):
            x = random.randint(1,self.GAME_WIDTH/self.SPACE_SIZE)*self.SPACE_SIZE
            y = random.randint(1,self.GAME_HEIGHT/self.SPACE_SIZE)*self.SPACE_SIZE
            while((x>(self.player.coordinates[0] + 200) and x<(self.player.coordinates[0] - 200)) and (y<self.player.coordinates[1] + 200 or y>self.player.coordinates[1] - 200)):
                x = random.randint(1,self.GAME_WIDTH/self.SPACE_SIZE)*self.SPACE_SIZE
                y = random.randint(1,self.GAME_HEIGHT/self.SPACE_SIZE)*self.SPACE_SIZE

            z = Zombie(self.score, self.player.coordinates, self.GAME_WIDTH, self.GAME_HEIGHT, self.RADIUS, self.SPACE_SIZE, self.gameboard, True)
            self.zombies.append(z)
            self.gameboard[int(z.coordinates[0]/self.SPACE_SIZE)][int(z.coordinates[1]/self.SPACE_SIZE)] = 2

    def in_bounds_x(self, x):
        if(x <= 0 or x > self.GAME_WIDTH):
            return False
        else:
            return True

    def in_bounds_y(self, y):
        if(y <= 0 or y > self.GAME_HEIGHT):
            return False
        else:
            return True

    def next_turn(self):
        x,y = self.player.coordinates

        #Move Player
        self.gameboard[int(x/self.SPACE_SIZE)][int(y/self.SPACE_SIZE)] = 0
        if self.direction == 1 and self.in_bounds_y(y-self.SPACE_SIZE):
            #up
            y-=self.SPACE_SIZE
        elif self.direction == 2 and self.in_bounds_y(y+self.SPACE_SIZE):
            #down
            y+=self.SPACE_SIZE       
        elif self.direction == 3 and self.in_bounds_x(x-self.SPACE_SIZE):
            #left
            x-=self.SPACE_SIZE  
        elif self.direction == 4 and self.in_bounds_x(x+self.SPACE_SIZE):
            #right
            x+=self.SPACE_SIZE  
        self.gameboard[int(x/self.SPACE_SIZE)][int(y/self.SPACE_SIZE)] = 1
        self.player.move(x,y)

        if self.check_collisions(x, y):
            gameinfo = {
                "alive": False,
                "info": GameInformation(self.score, self.look_forward())
            }
            return gameinfo
        else:
            #Player not dead, add score
            self.score += 1

            if(self.KILL_ZOMBIES):
                self.kill_zombies()
            if(self.score % self.ZOMBIE_SPEED == 0):
                kill = self.move_zombies()

                if(kill):
                    gameinfo = {
                        "alive": False,
                        "info": GameInformation(self.score, self.look_forward())
                    }
                    return gameinfo
                    
            #Return Game Information
            available = self.look_forward()
            gameinfo = {
                "alive": True,
                "info": GameInformation(self.score, available)
            }
            return gameinfo

    def move_zombies(self):
        kill = False
        x,y = self.player.coordinates
        
        for zombie in self.zombies:
            zx, zy = zombie.coordinates
            deltaX = x - zx
            deltaY = y - zy
            if (deltaX < 0 and deltaY > 0):
                #left/down
                if (not self.zombie_is_in_location(zx - self.SPACE_SIZE, zy + self.SPACE_SIZE)) and zy + self.SPACE_SIZE <= self.GAME_HEIGHT and zx - self.SPACE_SIZE > 0:
                    zombie.coordinates = [zx - self.SPACE_SIZE, zy + self.SPACE_SIZE]
            elif(deltaX < 0 and deltaY == 0):
                #left
                if not self.zombie_is_in_location(zx - self.SPACE_SIZE, zy) and zx - self.SPACE_SIZE > 0:
                    zombie.coordinates = [zx - self.SPACE_SIZE , zy]
            elif (deltaX < 0 and deltaY < 0):
                #left/up
                if not self.zombie_is_in_location(zx - self.SPACE_SIZE, zy - self.SPACE_SIZE) and zy - self.SPACE_SIZE > 0 and zx - self.SPACE_SIZE > 0:
                    zombie.coordinates = [zx - self.SPACE_SIZE, zy - self.SPACE_SIZE]
            elif(deltaX == 0 and deltaY < 0):
                #Up
                if not self.zombie_is_in_location(zx, zy - self.SPACE_SIZE) and zy - self.SPACE_SIZE > 0:
                    zombie.coordinates = [zx , zy - self.SPACE_SIZE]
            elif (deltaX > 0 and deltaY < 0):
                #right/up
                if not self.zombie_is_in_location(zx + self.SPACE_SIZE, zy - self.SPACE_SIZE) and zy - self.SPACE_SIZE > 0 and zx + self.SPACE_SIZE <= self.GAME_WIDTH:
                    zombie.coordinates = [zx + self.SPACE_SIZE, zy - self.SPACE_SIZE]
            elif(deltaX > 0 and deltaY == 0):
                #right
                if not self.zombie_is_in_location(zx + self.SPACE_SIZE, zy) and zx + self.SPACE_SIZE <= self.GAME_WIDTH:
                    zombie.coordinates = [zx + self.SPACE_SIZE, zy]
            elif (deltaX > 0 and deltaY > 0):
                #right/down
                if not self.zombie_is_in_location(zx + self.SPACE_SIZE, zy + self.SPACE_SIZE) and zy + self.SPACE_SIZE <= self.GAME_HEIGHT and zx + self.SPACE_SIZE <= self.GAME_WIDTH:
                    zombie.coordinates = [zx + self.SPACE_SIZE, zy + self.SPACE_SIZE]
            elif(deltaX == 0 and deltaY > 0):
                #down
                if not self.zombie_is_in_location(zx, zy + self.SPACE_SIZE) and zy + self.SPACE_SIZE <= self.GAME_HEIGHT:
                    zombie.coordinates = [zx , zy + self.SPACE_SIZE]

            self.gameboard[int(zx/self.SPACE_SIZE)][int(zy/self.SPACE_SIZE)] = 0
            if(self.gameboard[int(zombie.coordinates[0]/self.SPACE_SIZE)][int(zombie.coordinates[1]/self.SPACE_SIZE)] == 1):
                kill = True
            self.gameboard[int(zombie.coordinates[0]/self.SPACE_SIZE)][int(zombie.coordinates[1]/self.SPACE_SIZE)] = 2

        return kill

    def zombie_is_in_location(self, x, y):
        if(self.gameboard[int(x/self.SPACE_SIZE)][int(y/self.SPACE_SIZE)] == 2):
            return True
        return False

    def change_direction(self, new_direction):
        self.direction = new_direction

    def check_collisions(self, x, y):
        if(self.gameboard[int(x/self.SPACE_SIZE)][int(y/self.SPACE_SIZE)] == 2):
            return True
        return False

    def reset(self):
        self.score = 0
        self.direction = 1
        self.player = 0
        self.zombies = []    

    #Return 2 space in each direction of the player
    #0 = Nothing, 1 = Player, 2 = Zombie, 3 = Border
    #[0  1         2      3           4     5          6     7      ]
    #[UP,UP-RIGHT, RIGHT, DOWN-RIGHT, DOWN, DOWN-LEFT, LEFT, LEFT-UP]
    def look_around(self):
        x,y = self.player.coordinates
        x = int(x/self.SPACE_SIZE)
        y = int(y/self.SPACE_SIZE)

        available = [0,0,0,0,0,0,0,0,0]
        available = [
            self.gameboard[x][y-1],
            self.gameboard[x+1][y-1],
            self.gameboard[x+1][y],
            self.gameboard[x+1][y+1],
            self.gameboard[x][y+1],
            self.gameboard[x-1][y+1],
            self.gameboard[x-1][y],
            self.gameboard[x-1][y-1]
        ]

        #check edges
        if(x-1 == 0):
            available[1] = 3
            available[2] = 3
            available[3] = 3
        if(x*self.SPACE_SIZE == self.GAME_WIDTH):
            available[5] = 3
            available[6] = 3
            available[7] = 3
        if(y-1 == 0):
            available[7] = 3
            available[0] = 3
            available[1] = 3
        if(y*self.SPACE_SIZE == self.GAME_HEIGHT):
            available[3] = 3
            available[4] = 3
            available[5] = 3

        print(available)

        return available

    #Return 2 space in each direction of the player
    #0 = Nothing, 1 = Player, 2 = Zombie, 3 = Border
    #[0  1         2      3           4     5          6     7      ]
    #[UP,UP-RIGHT, RIGHT, DOWN-RIGHT, DOWN, DOWN-LEFT, LEFT, LEFT-UP]
    def look_forward(self):
        x,y = self.player.coordinates
        x = int(x/self.SPACE_SIZE)
        y = int(y/self.SPACE_SIZE)

        available = [0,0,0,0,0,0,0,0]

        #Up
        if(y-1 == 0):
            available[0] = 3
            available[1] = 3
        elif(y-2 == 0):
            available[0] = self.gameboard[x][y-1]
            available[1] = 3
        else:
            available[0] = self.gameboard[x][y-1]
            available[1] = self.gameboard[x][y-2]

        #Right
        if((x)*self.SPACE_SIZE == self.GAME_WIDTH):
            available[2] = 3
            available[3] = 3
        elif((x+1)*self.SPACE_SIZE == self.GAME_WIDTH):
            available[2] = self.gameboard[x+1][y]
            available[3] = 3
        else:
            available[2] = self.gameboard[x+1][y]
            available[3] = self.gameboard[x+2][y]

        #Down
        if((y)*self.SPACE_SIZE == self.GAME_HEIGHT):
            available[4] = 3
            available[5] = 3
        elif((y+1)*self.SPACE_SIZE == self.GAME_HEIGHT):
            available[4] = self.gameboard[x][y+1]
            available[5] = 3
        else:
            available[4] = self.gameboard[x][y+1]
            available[5] = self.gameboard[x][y+2]

        #Left
        if(x-1 == 0):
            available[6] = 3
            available[7] = 3
        elif(x-2 == 0):
            available[6] = self.gameboard[x-1][y]
            available[7] = 3
        else:
            available[6] = self.gameboard[x-1][y]
            available[7] = self.gameboard[x-2][y]

        return available



