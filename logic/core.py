import pygame
import sys
import os
import random
import tkinter as tk
from tkinter import filedialog

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
# TAG IMPLEMENTATION
from collision import circle_rect_collision
from particles import ParticleEmitter 

class Game:
    def __init__(self):
        pygame.init()

        # GAME STATES
        self.paused = False
        self.in_menu = True
        self.menu_state = "MAIN" # Possible states: MAIN, CUSTOM_SELECT, CUSTOM_EDIT, MAP_SELECT
        self.menu_selection = 0   
        self.player_to_edit = 0  # 0 for P1, 1 for P2
        
        # MAP LIST
        self.available_maps = [
            {"name": "ARENA CLASSIC", "path": "assets/maps/lv1.tmj"},
            {"name": "THE CAVE", "path": "assets/maps/lv2.tmj"}, 
            {"name": "EMPTY SLAG", "path": "assets/maps/lv3.tmj"}
        ]
        self.selected_map_idx = 0
    
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("J2D - Ultimate Tag")
        
        try:
            self.background = pygame.transform.scale(
                pygame.image.load("assets/2 Background/Background.png"),
                (SCREEN_WIDTH, SCREEN_HEIGHT)
            )
        except:
            self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.background.fill((30, 30, 30))

        self.particles = ParticleEmitter()

        # Players initialization
        self.players = [
            Player(500, 500, controls={"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "drop": pygame.K_s},
                   color=(255, 50, 50), is_tagger=True),
            Player(300, 100, controls={"left": pygame.K_LEFT, "right": pygame.K_RIGHT, "jump": pygame.K_UP, "drop": pygame.K_DOWN},
                   color=(50, 50, 255), is_tagger=False)
        ]

        self.clock = pygame.time.Clock()
        self.running = True
        
        # Load default map (will be overwritten when starting the game)
        self.level = Level(self.available_maps[0]["path"], "assets/maps/tileset_lv1.png")

    def open_image_picker(self):
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg")])
        root.destroy()
        if file_path:
            return pygame.image.load(file_path).convert_alpha()
        return None

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.in_menu:
                if event.type == pygame.KEYDOWN:
                    # --- MAIN MENU ---
                    if self.menu_state == "MAIN":
                        if event.key == pygame.K_UP: self.menu_selection = (self.menu_selection - 1) % 3
                        if event.key == pygame.K_DOWN: self.menu_selection = (self.menu_selection + 1) % 3
                        if event.key == pygame.K_RETURN:
                            if self.menu_selection == 0: self.menu_state = "MAP_SELECT"
                            elif self.menu_selection == 1: self.menu_state = "CUSTOM_SELECT"
                            elif self.menu_selection == 2: self.running = False

                    # --- PLAYER SELECTION FOR CUSTOMIZATION ---
                    elif self.menu_state == "CUSTOM_SELECT":
                        if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                            self.player_to_edit = 1 if self.player_to_edit == 0 else 0
                        if event.key == pygame.K_RETURN:
                            self.menu_state = "CUSTOM_EDIT"
                        if event.key == pygame.K_ESCAPE:
                            self.menu_state = "MAIN"

                    # --- PLAYER EDITION (IMAGE/COLOR) ---
                    elif self.menu_state == "CUSTOM_EDIT":
                        p = self.players[self.player_to_edit]
                        if event.key == pygame.K_i:
                            img = self.open_image_picker()
                            if img: p.custom_image = img
                        if event.key == pygame.K_c:
                            p.color = (random.randint(50,255), random.randint(50,255), random.randint(50,255))
                            p.custom_image = None
                        if event.key == pygame.K_ESCAPE:
                            self.menu_state = "CUSTOM_SELECT"

                    # --- MAP SELECTION ---
                    elif self.menu_state == "MAP_SELECT":
                        if event.key == pygame.K_UP: self.selected_map_idx = (self.selected_map_idx - 1) % len(self.available_maps)
                        if event.key == pygame.K_DOWN: self.selected_map_idx = (self.selected_map_idx + 1) % len(self.available_maps)
                        if event.key == pygame.K_RETURN:
                            # Load selected map and start game
                            m_data = self.available_maps[self.selected_map_idx]
                            self.level = Level(m_data["path"], "assets/maps/tileset_lv1.png")
                            self.in_menu = False 
                        if event.key == pygame.K_ESCAPE:
                            self.menu_state = "MAIN"
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.paused = not self.paused
                    if self.paused and event.key == pygame.K_q:
                        self.__init__() # Reset game state

    def update(self):
        for p in self.players:
            p.update(self.level.walls, FIXED_DT, self.particles)
        
        self.particles.update(FIXED_DT)

        # Tag Logic
        tagger = next((p for p in self.players if p.is_tagger), None)
        runner = next((p for p in self.players if not p.is_tagger), None)
        if tagger and runner and runner.tagback_cooldown == 0:
            if circle_rect_collision(tagger.rect.center, tagger.tag_radius, runner.rect):
                tagger.is_tagger, runner.is_tagger = False, True
                tagger.tagback_cooldown = tagger.tagback_cooldown_time

    def draw_menu(self):
        self.screen.fill((20, 20, 20))
        font_title = pygame.font.SysFont("Arial", 60, bold=True)
        font_ui = pygame.font.SysFont("Arial", 40, bold=True)
        
        if self.menu_state == "MAIN":
            options = ["START GAME", "CUSTOMIZE PLAYERS", "EXIT"]
            for i, opt in enumerate(options):
                color = (255, 255, 0) if i == self.menu_selection else (255, 255, 255)
                txt = font_ui.render(opt, True, color)
                self.screen.blit(txt, (100, 300 + i * 80))
        
        elif self.menu_state == "CUSTOM_SELECT":
            title = font_title.render("SELECT PLAYER", True, (255, 255, 255))
            self.screen.blit(title, (100, 100))
            for i in range(2):
                color = (255, 255, 0) if i == self.player_to_edit else (255, 255, 255)
                txt = font_ui.render(f"PLAYER {i+1}", True, color)
                self.screen.blit(txt, (200, 300 + i * 150))
                # Player preview
                self.players[i].rect.center = (100, 320 + i * 150)
                self.players[i].draw(self.screen)

        elif self.menu_state == "CUSTOM_EDIT":
            title = font_title.render(f"PLAYER {self.player_to_edit + 1}", True, (255, 255, 255))
            info = font_ui.render("[I] Image | [C] Color | [ESC] Back", True, (150, 150, 150))
            self.screen.blit(title, (100, 50))
            self.screen.blit(info, (100, 120))
            # Central preview
            p = self.players[self.player_to_edit]
            p.rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
            # update_animation might need vel_x, passing 0 for static preview
            if hasattr(p, 'update_animation'):
                p.update_animation(0) 
            p.draw(self.screen)

        elif self.menu_state == "MAP_SELECT":
            title = font_title.render("SELECT MAP", True, (255, 255, 255))
            self.screen.blit(title, (100, 100))
            for i, m in enumerate(self.available_maps):
                color = (255, 255, 0) if i == self.selected_map_idx else (255, 255, 255)
                txt = font_ui.render(m["name"], True, color)
                self.screen.blit(txt, (150, 300 + i * 70))

        pygame.display.flip()

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.level.draw(self.screen)
        self.particles.draw(self.screen)
        for p in self.players:
            p.draw(self.screen)
        if self.paused:
            # Pause overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0,0))
            font = pygame.font.SysFont("Arial", 50, bold=True)
            txt = font.render("PAUSED (Q to Quit)", True, (255, 255, 255))
            self.screen.blit(txt, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2))
        pygame.display.flip()

    def run(self):
        accumulator = 0.0
        last_time = pygame.time.get_ticks() / 1000.0

        while self.running:
            now = pygame.time.get_ticks() / 1000.0
            frame_time = min(now - last_time, 0.25)
            last_time = now
            accumulator += frame_time

            self.handle_events()

            if self.in_menu:
                self.draw_menu()
            else:
                if not self.paused:
                    # Physics update with fixed time step
                    while accumulator >= FIXED_DT:
                        self.update()
                        accumulator -= FIXED_DT
                    self.draw()
                else:
                    self.draw() # Still draw the game while paused

            self.clock.tick(RENDER_FPS)
        pygame.quit()
        sys.exit()
