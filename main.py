import pygame
import os
import random
import sys
import math
import neat

pygame.init()


#constants
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

#image imports from Assests folder
RUNNING = [pygame.image.load(os.path.join("Assets/Dino", "DinoRun1.png")),
           pygame.image.load(os.path.join("Assets/Dino", "DinoRun2.png"))]

JUMPING = pygame.image.load(os.path.join("Assets/Dino", "DinoJump.png"))

DUCKING = [pygame.image.load(os.path.join("Assets/Dino", "DinoSlide.png")),
           pygame.image.load(os.path.join("Assets/Dino", "DinoSlide2.png"))]

BG = pygame.image.load(os.path.join("Assets/Other", "Track.png"))

SMALL_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus1.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus3.png"))]

LARGE_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus1.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus3.png"))]

FLYING_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "FlyingCactus.png"))]

FONT = pygame.font.Font('freesansbold.ttf', 20)

class Dinosaur:
    X_POS = 80
    Y_POS = 310
    JUMP_VEL = 8.5

    def __init__(self, img=RUNNING[0]):
        self.image = img
        self.dino_run = True #true bc dino should run on its own from the start
        self.dino_jump = False #false bc should not be jumping randomly
        self.dino_duck = False
        self.jump_vel = self.JUMP_VEL
        self.rect = pygame.Rect(self.X_POS, self.Y_POS, img.get_width(), img.get_height()) #draws rectangle around dino for hitbox
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) #gives dino its random color
        self.step_index = 0 #loops thoguh index so we can get the running dino animation

    def update(self):
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()
        if self.dino_duck:
            self.duck()
        if self.step_index >= 10:
            self.step_index = 0 #reset for step index

    def jump(self):
        self.image = JUMPING
        if self.dino_jump:
            self.rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        if self.jump_vel <= -self.JUMP_VEL: #if velocity <= -8.5, go back to run
            self.dino_jump = False
            self.dino_duck = False
            self.dino_run = True
            self.jump_vel = self.JUMP_VEL
    
    def duck(self):
        self.image = DUCKING[self.step_index // 5]
        self.rect.x = self.X_POS
        self.rect.y = 348
        self.step_index += 1
    
    def run(self):
        self.image = RUNNING[self.step_index // 5] #first 5 counts is the first frame of dino run, next 5 is the second frame
        self.rect.x = self.X_POS
        self.rect.y = self.Y_POS
        self.step_index += 1


    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.rect.x, self.rect.y)) #draws dino
        pygame.draw.rect(SCREEN, self.color, (self.rect.x, self.rect.y, self.rect.width, self.rect.height), 2) #draws hitbox
        for obstacle in obstacles:
            pygame.draw.line(SCREEN, self.color, (self.rect.x + 54, self.rect.y + 12), obstacle.rect.center, 2) #draws line of sight to obsticles

class Obstacle:
    def __init__(self, image, number_of_cacti, type):
        self.image = image
        self.type = number_of_cacti #catus image 1 2 or 3
        self.rect = self.image[self.type].get_rect() # hitbox
        self.rect.x = SCREEN_WIDTH #xcordinate

    def update(self): #moving right to left
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            obstacles.pop()#deletes it after it goes off the screen
    
    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)

class SmallCactus(Obstacle): #inherits from obsticle class
    def __init__(self, image, number_of_cacti, type):
        super().__init__(image, number_of_cacti, type)
        self.rect.y = 325
        self.passed = False


class LargeCactus(Obstacle):
    def __init__(self, image, number_of_cacti, type):
        super().__init__(image, number_of_cacti, type)
        self.rect.y = 300
        self.passed = False

class FlyingCactus(Obstacle):
    def __init__(self, image, number_of_cacti, type):
        super().__init__(image, number_of_cacti, type)
        self.rect.y = 80
        self.rect.width = self.rect.width/2
        self.passed = False

def remove(index): 
    dinosaurs.pop(index) #removes dinosaurs after they hit an obstacle
    ge.pop(index) #removes its genomes
    nets.pop(index) # removes its neural networks

def distance(pos_a, pos_b):
    dx = pos_a[0]-pos_b[0]
    dy = pos_a[1]-pos_b[1]
    return math.sqrt(dx**2+dy**2)

def eval_genomes(genomes, config): #takes care of the evolution of the dinsaurs genomes, param genomes, param config is the config file
    global game_speed, x_pos_bg, y_pos_bg, obstacles, dinosaurs, ge, nets, points
    clock = pygame.time.Clock()
    points = 0

    obstacles = [] #stores list of obstacles on screen
    dinosaurs = [] #list of dinosaurs, can be expanded for the many gens of dinos for NEAT Learning
    ge = [] #stores dictionaries on info of each dino like its fitness level, its nodes, and its connections
    nets = [] #stores neural nets object of each dino

    x_pos_bg = 0
    y_pos_bg = 380 # raises the ya ya ya
    game_speed = 20

    for genome_id, genome in genomes: #loops through all dinos in the population
        dinosaurs.append(Dinosaur()) #gives it the dinosaur object
        ge.append(genome) #gives it a genome
        net = neat.nn.FeedForwardNetwork.create(genome, config) 
        nets.append(net) #gives it a neural net
        genome.fitness = 0 #every genome starts at 0

    def score(): #when called, it will up the score by one
        global points, game_speed
        points += 1
        if points % 100 == 0: #every hundred score the game speed goe up one to make it harder
            game_speed += 1
        text = FONT.render(f'Points:  {str(points)}', True, (0, 0, 0))
        SCREEN.blit(text, (950, 50)) #shows it on the screen

    def statistics(): #displays statistics
        global dinosaurs, game_speed, ge
        text_1 = FONT.render(f'Dinosaurs Alive:  {str(len(dinosaurs))}', True, (0, 0, 0))
        text_2 = FONT.render(f'Generation:  {pop.generation+1}', True, (0, 0, 0))
        text_3 = FONT.render(f'Game Speed:  {str(game_speed)}', True, (0, 0, 0))

        SCREEN.blit(text_1, (50, 450))
        SCREEN.blit(text_2, (50, 480))
        SCREEN.blit(text_3, (50, 510))

    def background(): #makes the background look like its moving
        global x_pos_bg, y_pos_bg
        image_width = BG.get_width()
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        if x_pos_bg <= -image_width:
            x_pos_bg = 0
        x_pos_bg -= game_speed



    run = True
    while run: #Checking to see if we quit the program
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        SCREEN.fill((255, 255, 255))

        for dinosaur in dinosaurs:
            dinosaur.update()
            dinosaur.draw(SCREEN)
        
        if len(obstacles) == 0:
            rand_int = random.randint(0, 6) #big, small, or flying cactus
            if 0<=rand_int<3:
                obstacles.append(SmallCactus(SMALL_CACTUS, random.randint(0, 2), 0))
            elif 3<=rand_int<5:
                obstacles.append(LargeCactus(LARGE_CACTUS, random.randint(0, 2), 0))
            elif rand_int == 6:
                obstacles.append(FlyingCactus(FLYING_CACTUS, 0, 1))

        if len(dinosaurs) == 0: #if all dinos dead
            break

        for obstacle in obstacles:
            obstacle.draw(SCREEN)
            obstacle.update()
            for i, dinosaur in enumerate(dinosaurs): #checks all dinos
                if dinosaur.rect.colliderect(obstacle.rect): #if a dino hitbox hits a cactus hitbox
                    ge[i].fitness -= 1 #lowers fitness score for dying
                    remove(i) #kill the dino that did
                if dinosaur.rect.x > obstacle.rect.x and not obstacle.passed:
                    genome.fitness += 1  # Reward for passing an obstacle
                    obstacle.passed = True  # Ensure this is only rewarded once

        for i, dinosaur in enumerate(dinosaurs):        
            if(len(obstacles) != 0):
                output = nets[i].activate((dinosaur.rect.y, distance((dinosaur.rect.x, dinosaur.rect.y), obstacle.rect.midtop),
                                            obstacle.type)) #pass inputs of each dinosaur, ypos and dist to next obstacle
                action = output.index(max(output))  # Determine the action based on the highest output value
            else:
                action = 2 
            if action == 0 and dinosaur.rect.y >= 310:  # Jump
                dinosaur.rect.y = dinosaur.Y_POS
                dinosaur.dino_jump = True
                dinosaur.dino_duck = False
                dinosaur.dino_run = False
            elif action == 1 and dinosaur.rect.y >= 310:  # Duck
                dinosaur.dino_jump = False
                dinosaur.dino_duck = True
                dinosaur.dino_run = False
            elif action == 2 and dinosaur.rect.y >= 310:  # Run
                dinosaur.dino_jump = False
                dinosaur.dino_duck = False
                dinosaur.dino_run = True

        statistics()
        score()
        background()
        clock.tick(30)
        pygame.display.update()

#setup for the neat algo
def run(config_path): #gets path to config.txt
    global pop
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    pop = neat.Population(config) #gets populating from the config file
    pop.run(eval_genomes, 50) #run evolution(fitness) function 50 times

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    run(config_path)