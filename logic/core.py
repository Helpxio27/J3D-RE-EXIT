import pygame
import sys
# ALL settings
from settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FIXED_DT,
    RENDER_FPS,
    BACKGROUND_COLOR
)
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

        # MENU TESTING FUNCTIONALITY
        self.paused = False
        self.in_menu = True
    
        # Screen Making, and showing
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # Create the game window
        pygame.display.set_caption("My First Platformer") # Set the window title
        
        self.background = pygame.transform.scale(
            pygame.image.load("assets/2 Background/Background.png"),
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )

        # FPS SHOWER
        self.fps_timer = 0.0
        self.fps_frames = 0

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
        accumulator = 0.0
        last_time = pygame.time.get_ticks() / 1000.0

        while self.running:
            now = pygame.time.get_ticks() / 1000.0
            frame_time = now - last_time
            last_time = now
            self.render_dt = frame_time

            # wha?
            frame_time = min(frame_time, 0.25)

            accumulator += frame_time

            self.handle_events()

            if self.in_menu:
                self.draw_menu()

            else:
                if not self.paused:
                    while accumulator >= FIXED_DT:
                        self.update()
                        accumulator -= FIXED_DT
                    self.draw()
                else:
                    self.draw_pause_overlay()

            # FPS COUNTER (render FPS)
            self.fps_timer += frame_time
            self.fps_frames += 1

            if self.fps_timer >= 1.0:
                print(f"FPS: {self.fps_frames}")
                self.fps_timer -= 1.0
                self.fps_frames = 0

            self.clock.tick(RENDER_FPS) 

        self.quit()
    
    def update(self):
        # 1. Update all players
        for p in self.players:
            p.update(self.level.walls, self.render_dt)

        # 2. Tag logic (to put somewhere else in the future)
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
    
    def draw_menu(self):
        self.screen.fill((20, 20, 20))
        font = pygame.font.SysFont(None, 48)
        text = font.render("ENTER = Play | ESC = Quit", True, (255, 255, 255))
        self.screen.blit(text, (100, 100))
        pygame.display.flip()

    def draw_pause_overlay(self):
        font = pygame.font.SysFont(None, 48)
        text = font.render("PAUSED | ESC = Resume | Q = Menu", True, (255, 255, 255))
        self.screen.blit(text, (100, 100))
        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # MENU controls (when in menu)
            elif self.in_menu and event.type == pygame.KEYDOWN: 
                if event.key == pygame.K_RETURN:
                    self.in_menu = False
                elif event.key == pygame.K_ESCAPE:
                    self.running = False

            # GAME controls (when not in menu, you can pause with esc, and go back to menu with q)
            elif not self.in_menu and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.paused = not self.paused
                if self.paused and event.key == pygame.K_q:
                    self.reset_to_menu()
    def reset_to_menu(self):
        self.in_menu = True
        self.paused = False

        # Recreate game state cleanly
        self.__init__()

        # TEMPORARY CODE

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
