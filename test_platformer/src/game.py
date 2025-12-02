import pygame
from settings import *
from .level import Level

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Platformer")
        self.clock = pygame.time.Clock()

        self.level = Level("data/levels/level1.csv")

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.level.update()
            self.level.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(FPS)

