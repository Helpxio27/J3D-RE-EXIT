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

        self.colliders = [ pygame.Rect(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40),   # sol
                        pygame.Rect(0, 0, 40, SCREEN_HEIGHT),                  # mur gauche
                        pygame.Rect(SCREEN_WIDTH - 40, 0, 40, SCREEN_HEIGHT),  # mur droit
                        pygame.Rect(0, 0, SCREEN_WIDTH, 40),                   # plafond
                        pygame.Rect(300, 350, 200, 30),
                        pygame.Rect(500, 200, 40, 200), # ce sont des obstacles internes si vous voulez testez
                        ]
    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()

        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        self.player.update(self.colliders)     # Passe les colliders pour collision et wall slide/jump
    
    
    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        
        for c in self.colliders:              # Dessin des colliders
            pygame.draw.rect(self.screen, (220, 220, 220), c)
        
        self.player.draw(self.screen)          # Dessin du joueur
        pygame.display.flip()
    

