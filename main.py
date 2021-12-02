import neat
import pygame
import os
import random
import sys
import math

pygame.init()

HIGH_SCORE = 0
SCREEN_HEIGHT = 720
SCREEN_WIDTH = 1280
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

RUNNING = [pygame.image.load(os.path.join("DinoGameAssets/Dino", "DinoRun1.png")),
           pygame.image.load(os.path.join("DinoGameAssets/Dino", "DinoRun2.png"))]

JUMPING = pygame.image.load(os.path.join("DinoGameAssets/Dino", "DinoJump.png"))

BG = pygame.image.load(os.path.join("DinoGameAssets/Other", "Track.png"))

SMALL_CACTUS = [pygame.image.load(os.path.join("DinoGameAssets/Cactus", "SmallCactus1.png")),
                pygame.image.load(os.path.join("DinoGameAssets/Cactus", "SmallCactus2.png")),
                pygame.image.load(os.path.join("DinoGameAssets/Cactus", "SmallCactus3.png"))]
LARGE_CACTUS = [pygame.image.load(os.path.join("DinoGameAssets/Cactus", "LargeCactus1.png")),
                pygame.image.load(os.path.join("DinoGameAssets/Cactus", "LargeCactus2.png")),
                pygame.image.load(os.path.join("DinoGameAssets/Cactus", "LargeCactus3.png"))]

FONT = pygame.font.Font('freesansbold.ttf', 20)


class Dinosaur:
    X_POS = 80
    Y_POS = 310
    JUMP_VEL = 8.5

    def __init__(self, img=RUNNING[0]):
        self.image = img
        self.dino_run = True
        self.dino_jump = False
        self.jump_vel = self.JUMP_VEL
        self.rect = pygame.Rect(self.X_POS, self.Y_POS, img.get_width(), img.get_height())
        self.step_index = 0
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def update(self):
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()
        if self.step_index >= 10:
            self.step_index = 0

    def jump(self):
        self.image = JUMPING
        if self.dino_jump:
            self.rect.y -= self.jump_vel * 4
            self.jump_vel -= .8
        if self.jump_vel <= -self.JUMP_VEL:
            self.dino_jump = False
            self.dino_run = True
            self.jump_vel = self.JUMP_VEL

    def run(self):
        self.image = RUNNING[self.step_index // 5]
        self.rect.x = self.X_POS
        self.rect.y = self.Y_POS
        self.step_index += 1

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.rect.x, self.rect.y))
        pygame.draw.rect(SCREEN, self.color, (self.rect.x, self.rect.y,
                         self.rect.width, self.rect.height), 2)
        for cacti in obstacles:
            pygame.draw.line(SCREEN, self.color, (self.rect.x + 53,
                             self.rect.y + 11), cacti.rect.center, 2)

class Cacti:
    def __init__(self, image, number_cacti):
        self.image = image
        self.type = number_cacti
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH

    def update(self):
        self.rect.x -= speed
        if self.rect.x < -self.rect.width:
            obstacles.pop()

    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)

class SmallCactus(Cacti):
    def __init__(self, image, number_cacti):
        super().__init__(image, number_cacti)
        self.rect.y = 325

class BigCactus(Cacti):
    def __init__(self, image, number_cacti):
        super().__init__(image, number_cacti)
        self.rect.y = 300

def remove(index):
    dinos.pop(index)
    g.pop(index)
    nets.pop(index)

def eval_genomes(genomes, config):
    global speed, x_bg_pos, y_bg_pos, obstacles, dinos, points, nets, g, HIGH_SCORE
    time = pygame.time.Clock()
    points = 0
    x_bg_pos = 0;
    y_bg_pos = 380;
    speed = 20

    obstacles = []
    dinos = []
    g = []
    nets = []

    for genome_id, genome in genomes:
        dinos.append(Dinosaur())
        g.append(genome)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0

    def score():
        global points, speed, HIGH_SCORE
        points += 1
        if points % 100 == 0:
            speed += 1
        current_score = FONT.render(f'Score:  {str(points)}', True, (0, 0, 0))
        high = FONT.render(f'High Score:  {str(HIGH_SCORE)}', True, (0, 0, 0))
        SCREEN.blit(current_score, (1050, 20))
        SCREEN.blit(high, (1050, 50))

    def bg():
        global x_bg_pos, y_bg_pos
        image_width = BG.get_width()
        SCREEN.blit(BG, (x_bg_pos, y_bg_pos))
        SCREEN.blit(BG, (image_width + x_bg_pos, y_bg_pos))
        if x_bg_pos <= -image_width:
            x_bg_pos = 0
        x_bg_pos -= speed

    def distance(a_pos, b_pos):
        dx = a_pos[0] - b_pos[0]
        dy = a_pos[1] - b_pos[1]
        return math.sqrt(dx ** 2 + dy ** 2)

    def dino_stats():
        global dinos, speed, g, HIGH_SCORE, points
        alive = FONT.render(f'Dinosaurs Alive:  {str(len(dinos))}', True, (0, 0, 0))
        generation = FONT.render(f'Generation:  {pop.generation + 1}', True, (0,0,0))
        gameSpeed = FONT.render(f'Game Speed:  {str(speed)}', True, (0, 0, 0))
        SCREEN.blit(alive, (1050, 80))
        SCREEN.blit(generation, (1050, 110))
        SCREEN.blit(gameSpeed, (1050, 140))
        if HIGH_SCORE < points:
                HIGH_SCORE = points

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        SCREEN.fill((255, 255, 255))

        for dinosaur in dinos:
            dinosaur.update()
            dinosaur.draw(SCREEN)

        if len(dinos) == 0:
            break

        if len(obstacles) == 0:
            rand_int = random.randint(0, 1)
            if rand_int == 0:
                obstacles.append(SmallCactus(SMALL_CACTUS, random.randint(0, 2)))
            elif rand_int == 1:
                obstacles.append(BigCactus(LARGE_CACTUS, random.randint(0, 2)))

        for cactus in obstacles:
            cactus.draw(SCREEN)
            cactus.update()
            for i, dino in enumerate(dinos):
                if dino.rect.colliderect(cactus.rect):
                    g[i].fitness -= 1
                    remove(i)



        for i, dinosaur in enumerate(dinos):
            output = nets[i].activate((dinosaur.rect.y, distance((dinosaur.rect.x,
                                      dinosaur.rect.y), cactus.rect.midtop)))
            if output[0] > 0.5 and dinosaur.rect.y == dinosaur.Y_POS:
                dinosaur.dino_jump = True
                dinosaur.dino_run = False

        dino_stats()
        score()
        bg()
        time.tick(30)
        pygame.display.update()

def run(config_path):
    global pop
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    pop = neat.Population(config)
    pop.run(eval_genomes, 50)

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    run(config_path)