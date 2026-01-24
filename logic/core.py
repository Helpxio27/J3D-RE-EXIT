import pygame
import sys
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BACKGROUND_COLOR
from player import Player
from level import Level
import os
# TAG IMPLEMENTATION
from collision import circle_rect_collision

# TILESET IMPLEMENTATION
import json

# Making sure the 
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller """
    try:
        # PyInstaller stores files in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath("..")  # adjust if main.py is in logic/

    return os.path.join(base_path, relative_path)

class Game:
    def __init__(self):
        pygame.init()
        # Screen Making, and showing
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # Create the game window
        pygame.display.set_caption("My First Platformer") # Set the window title
        
        self.background = pygame.transform.scale(
            pygame.image.load("assets/2 Background/Background.png"),
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )

        # Update Cycle
        # self.player = Player(300, 300)
        
        self.players = [
            Player(
                500, 500,
                controls={"left": pygame.K_a, 
                        "right": pygame.K_d, 
                        "jump": pygame.K_w,
                        "drop": pygame.K_s},
                color=(255, 50, 50),
                is_tagger=True
            ),
            Player(
                300, 100,
                controls={"left": pygame.K_LEFT, 
                        "right": pygame.K_RIGHT, 
                        "jump": pygame.K_UP, 
                        "drop": pygame.K_DOWN},
                color=(50, 50, 255),
                is_tagger=False
            )
        ]


        self.clock = pygame.time.Clock()
        self.running = True

        self.level = Level("assets/maps/lv1.tmj", "assets/maps/tileset_lv1.png")

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
        # 1. Update all players
        for p in self.players:
            p.update(self.level.walls)

        # 2. Tag logic
        tagger = None
        runner = None

        for p in self.players:
            if p.is_tagger:
                tagger = p
            else:
                runner = p

                
        if tagger and runner:
            # Only tag if runner is not immune from tagback
            if runner.tagback_cooldown == 0 and circle_rect_collision(
                tagger.rect.center,
                tagger.tag_radius,
                runner.rect
            ):
                # Swap roles
                tagger.is_tagger = False
                runner.is_tagger = True

                # Apply tagback cooldown to the old tagger
                tagger.tagback_cooldown = tagger.tagback_cooldown_time
    
    def draw(self):
        # self.screen.fill(BACKGROUND_COLOR)
        # Instead of screen.fill(...)
        self.screen.blit(self.background, (0, 0))
        for p in self.players:
            p.draw(self.screen)
        
        self.level.draw(self.screen)

        pygame.display.flip()

    def quit(self):
        pygame.quit()
        sys.exit()
