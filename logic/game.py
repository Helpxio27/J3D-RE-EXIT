import pygame
import sys
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BACKGROUND_COLOR
from player import Player

class Game:
    def __init__(self):
        pygame.init()
        # Screen Making, and showing
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # Create the game window
        pygame.display.set_caption("My First Platformer") # Set the window title
        
        # Update Cycle
        self.player = Player(100, 100)
        # Temporary floor
        self.floor_y = SCREEN_HEIGHT - 50

        self.clock = pygame.time.Clock()
        self.running = True

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()

        self.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        self.player.update() # Calls the function taking the inputs

        # Temporary floor collision
        if self.player.rect.bottom >= self.floor_y:
            self.player.rect.bottom = self.floor_y
            self.player.vel_y = 0
            self.player.on_ground = True

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        self.player.draw(self.screen)
        
        # Temporary visual floor
        pygame.draw.rect(
            self.screen,
            (244, 244, 244), 
            (0, self.floor_y, SCREEN_WIDTH, 50)
        )

        pygame.draw.rect(
            self.screen,
            (244, 244, 244), 
            (0, 70, 40, 50)
        )
        
        pygame.display.flip()

    def quit(self):
        pygame.quit()
        sys.exit()
