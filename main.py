from zombies import Game
from aStar import aStarAlg
import neat
import pygame
import os
import time
import pickle

class ZombieGame:
    def __init__(self, win, genome_stats={"test": '', "Genome ID": '', "fitness": '', "gen": ''}):
        self.game = Game(win, genome_stats)

    def test_ai(self, net):
        clock = pygame.time.Clock()
        display = True
        run = True
        still_count = 0
        prev_coordinates = [[0,0],[],[],[]]
        while run:
            clock.tick(24)
            game_info = self.game.next_turn()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    break

            input = game_info["info"].available_moves
            output = net.activate((input[0],input[1],input[2],input[3],input[4],input[5],input[6],input[7]))
            decision = output.index(max(output))

            if(game_info["alive"]):
                if decision == 1:
                    self.game.change_direction(1)
                elif decision == 2:
                    self.game.change_direction(2)
                elif decision == 3:
                    self.game.change_direction(3)
                elif decision  == 4:
                    self.game.change_direction(4)

                #Check if player has moved
                if(prev_coordinates[0] == self.game.player.coordinates or (prev_coordinates[2] == prev_coordinates[0] and prev_coordinates[3] == prev_coordinates[1])):
                    still_count+=1
                else:
                    still_count = 0
                
                #Track Last 4 moves
                for i in range(len(prev_coordinates)-1):
                    prev_coordinates[len(prev_coordinates)-i-1] = prev_coordinates[len(prev_coordinates)-i-2]
                prev_coordinates[0] = self.game.player.coordinates

                #Display Game Board
                if display:
                    self.game.draw(draw_score=True, draw_textures=False, print_stats = True)
                    pygame.display.update()
            else:
                run = False
            still_count += 1

        pygame.quit()
    
    def train_ai(self, genome, config):
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        run = True
        display = True
        clock = pygame.time.Clock()
        still_count = 0
        prev_coordinates = [[0,0],[],[],[]]
        while run:
            #clock.tick(30)
            game_info = self.game.next_turn()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()

            input = game_info["info"].available_moves
            output = net.activate((input[0],input[1],input[2],input[3],input[4],input[5],input[6],input[7]))
            decision = output.index(max(output))

            if(game_info["alive"] and still_count < 4 and game_info["info"].score <= 10000):
                if decision == 0:
                    self.game.change_direction(1)
                elif decision == 1:
                    self.game.change_direction(2)
                elif decision == 2:
                    self.game.change_direction(3)
                elif decision  == 3:
                    self.game.change_direction(4)
    
                #Check if player has moved
                if(prev_coordinates[0] == self.game.player.coordinates or (prev_coordinates[2] == prev_coordinates[0] and prev_coordinates[3] == prev_coordinates[1])):
                    still_count+=1
                else:
                    still_count = 0
                
                #Track Last 4 moves
                for i in range(len(prev_coordinates)-1):
                    prev_coordinates[len(prev_coordinates)-i-1] = prev_coordinates[len(prev_coordinates)-i-2]
                prev_coordinates[0] = self.game.player.coordinates

                #Display Game Board
                if display:
                    self.game.draw(draw_score=True, draw_textures=False, print_stats = True)
                    pygame.display.update()
            else:
                self.calculate_fitness(genome, game_info)
                run = False

    def test_aStar(self):
        clock = pygame.time.Clock()
        display = True
        run = True
        still_count = 0
        prev_coordinates = [[0,0],[],[],[]]
        ai = aStarAlg()

        while run:
            clock.tick(24)
            game_info = self.game.next_turn()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    break

            decision = ai.runAStar(self.game.gameboard, self.game.player.coordinates)

            if(game_info["alive"]):
                if decision == 1:
                    self.game.change_direction(1)
                elif decision == 2:
                    self.game.change_direction(2)
                elif decision == 3:
                    self.game.change_direction(3)
                elif decision  == 4:
                    self.game.change_direction(4)

                #Check if player has moved
                if(prev_coordinates[0] == self.game.player.coordinates or (prev_coordinates[2] == prev_coordinates[0] and prev_coordinates[3] == prev_coordinates[1])):
                    still_count+=1
                else:
                    still_count = 0
                
                #Track Last 4 moves
                for i in range(len(prev_coordinates)-1):
                    prev_coordinates[len(prev_coordinates)-i-1] = prev_coordinates[len(prev_coordinates)-i-2]
                prev_coordinates[0] = self.game.player.coordinates

                #Display Game Board
                if display:
                    self.game.draw(draw_score=True, draw_textures=False, print_stats = True)
                    pygame.display.update()
            else:
                run = False
            still_count += 1

        pygame.quit()

    def calculate_fitness(self, genome, game_info):
        genome.fitness += game_info["info"].score

generation = 1
def eval_genomes(genomes, config):
    global generation
    width, height = 1000, 700
    win = pygame.display.set_mode((width, height))
    for i, (genome_id, genome) in enumerate(genomes):
        genome.fitness = 0
        #Each Genome is test 10 times to reduce the effect of luck
        for j in range(10):
            genome_stats = {"test": j, "Genome ID": genome_id, "fitness": genome.fitness, "gen": generation}
            game = ZombieGame(win, genome_stats)
            game.train_ai(genome, config)
    generation += 1

def run_neat(config):
    #p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-*')
    p = neat.Population(config)
    
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(1))

    winner = p.run(eval_genomes, 1000)
    with open("best.pickle", "wb") as f:
        pickle.dump(winner, f)

def test_ai(config):
    with open("best.pickle", "rb") as f:
        winner = pickle.load(f)
    winner_net = neat.nn.FeedForwardNetwork.create(winner, config)

    width, height = 1000, 700
    window = pygame.display.set_mode((width, height))
    winner_net = neat.nn.FeedForwardNetwork.create(winner, config)

    game = ZombieGame(window)
    game.test_ai(winner_net)

def run_aStar():
    width, height = 1000, 700
    window = pygame.display.set_mode((width, height))

    game = ZombieGame(window)
    game.test_aStar()

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")

    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)
    #run_neat(config)
    #test_ai(config)
    run_aStar()