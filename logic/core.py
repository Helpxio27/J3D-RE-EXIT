import json

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
from level import Level
from level import MapRenderer
# TAG IMPLEMENTATION
from collision import circle_rect_collision # for tag
from particles import ParticleEmitter # for effects
from menu import Menu # Menu system

from player_sim import PlayerSim
from player_render import PlayerRender
import socket

# Making sure the it's the right path depending on the OS (for assets loading)
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller """
    try:
        # PyInstaller stores files in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Project root is parent of logic/
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    return os.path.join(base_path, relative_path)

    
class Game:
    def __init__(self):
        pygame.init()

        self.online = False  # toggle for online mode (not implemented yet)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(False)
        self.server_addr = ("localhost", 9999)





        # GAME STATES and MENU STATES
        self.paused = False
        self.in_menu = True
        self.menu_state = "MAIN" # Possible states: MAIN, CUSTOM_SELECT, CUSTOM_EDIT, MAP_SELECT
        self.menu_selection = 0   
        self.player_to_edit = 0  # 0 for P1, 1 for P2

        self.menu = Menu(self)

        # MAP LIST
        self.available_maps = [
            {"name": "ARENA CLASSIC", 
            "path": resource_path("assets/maps/lv1.tmj"), 
            "tileset": resource_path("assets/maps/tileset_lv1.png")},
            {"name": "THE CAVE", 
            "path": resource_path("assets/maps/lv2.tmj"), 
            "tileset": resource_path("assets/maps/tileset_lv2.png")},
            {"name": "TARIO", 
            "path": resource_path("assets/maps/lv3.tmj"), 
            "tileset": resource_path("assets/maps/tileset_lv3.png")}
        ]

        self.selected_map_idx = 0

        # ASSET LOADING (background, tilesets, etc.)  
        self.WIDTH, self.HEIGHT = SCREEN_WIDTH, SCREEN_HEIGHT
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        # Virtual screen at fixed resolution
        self.virtual_screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))


        pygame.display.set_caption("RE-EXIT - AAGHUAGHAUWHGAUHWGAUHWGUAWHGUAHGUAHGUAHGUAWHG")

        # Background
        try:
            self.background = pygame.transform.scale(
                pygame.image.load(resource_path("assets/2 Background/Background.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT)
            )
        except:
            self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.background.fill((30, 30, 30))
        
        self.particles = ParticleEmitter()

        # FPS SHOWER
        self.fps_timer = 0.0
        self.fps_frames = 0

        self.controls = [
            {"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "drop": pygame.K_s},
            {"left": pygame.K_LEFT, "right": pygame.K_RIGHT, "jump": pygame.K_UP, "drop": pygame.K_DOWN}
        ]

        self.spawn_points = [(500, 700), (500, 700)]
        self.player_sims = [
            PlayerSim(self.spawn_points[0][0], self.spawn_points[0][1], is_tagger=True),
            PlayerSim(self.spawn_points[1][0], self.spawn_points[1][1], is_tagger=False)
        ]

        self.player_renders = [
            PlayerRender((255,50,50)),
            PlayerRender((50,50,255))
        ]

        if len(self.controls) != len(self.player_sims):
            raise ValueError("Number of controls must match number of players")


        # # FPS THINGY
        # self.spawn_points = [(500, 700), (500, 700)]
        # self.players = [
        #     Player(self.spawn_points[0][0], self.spawn_points[0][1], 
        #            controls={"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_w, "drop": pygame.K_s},
        #            color=(255, 50, 50), is_tagger=True),
        #     Player(self.spawn_points[1][0], self.spawn_points[1][1], 
        #            controls={"left": pygame.K_LEFT, "right": pygame.K_RIGHT, "jump": pygame.K_UP, "drop": pygame.K_DOWN},
        #            color=(50, 50, 255), is_tagger=False)
        # ]

        self.clock = pygame.time.Clock()
        self.running = True

        # TILESET IMPLEMENTATION
        #self.level = Level("assets/maps/lv3.tmj", "assets/maps/tileset_lv3.png")
        #self.renderer = MapRenderer(self.level)

    def open_image_picker(self):
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg")])
        root.destroy()
        if file_path:
            return pygame.image.load(file_path).convert_alpha()
        return None

    def reset_players_position(self):
        """Reset players to their starting positions before the match begins"""
        for i, p in enumerate(self.player_sims):
            p.rect.center = self.spawn_points[i]
            p.vel_x = 0
            p.vel_y = 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.VIDEORESIZE:
                self.handle_resize(event.w, event.h)
            if self.in_menu:
                self.menu.handle_events(event)
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.paused = not self.paused
                    if self.paused and event.key == pygame.K_q:
                        self.reset_to_menu()

    def update(self, inputs_per_player):
        # 1. Update simulations ONLY
        for i, sim in enumerate(self.player_sims):
            # Inputs for this player (default to no input if not provided)
            inputs = inputs_per_player[i] if i < len(inputs_per_player) else {"left":False,"right":False,"jump":False,"drop":False}
            sim.update(self.level.walls, inputs) # walls + inputs for calculating new position and state

        # 2. Update render state (particles, animation, etc.)
        for i, render in enumerate(self.player_renders):
            render.update(self.render_dt, self.player_sims[i])

        # 3. Tag logic (unchanged)
        tagger = None
        runner = None

        for p in self.player_sims:
            if p.is_tagger:
                tagger = p
            else:
                runner = p

        if tagger and runner:
            if runner.tagback_cooldown == 0 and circle_rect_collision(
                tagger.rect.center,
                tagger.tag_radius,
                runner.rect
            ):
                tagger.is_tagger = False
                runner.is_tagger = True
                tagger.tagback_cooldown = tagger.tagback_cooldown_time
                runner.vel_x = 0
                runner.vel_y = 0
                runner.stun_timer = 10

    def run(self):
        accumulator = 0.0
        last_time = pygame.time.get_ticks() / 1000.0

        while self.running:
            now = pygame.time.get_ticks() / 1000.0
            frame_time = now - last_time
            last_time = now
            self.render_dt = frame_time
            frame_time = min(frame_time, 0.25)
            accumulator += frame_time
            self.handle_events()

            # Build per-player inputs **for this frame**
            inputs_per_player = []
            keys = pygame.key.get_pressed()

            for i, ctrl in enumerate(self.controls):
                inputs = {
                    "left": keys[ctrl["left"]],
                    "right": keys[ctrl["right"]],
                    "jump": keys[ctrl["jump"]],
                    "drop": keys[ctrl["drop"]],
                }
                inputs_per_player.append(inputs)

            if self.online:
                try:
                    msg = {
                        "input": inputs_per_player[0]  # assume player 0 is local
                    }
                    self.sock.sendto(json.dumps(msg).encode(), self.server_addr)
                except:
                    pass            

            # Debug print
            # print("Current inputs:", inputs_per_player)
            
            if self.in_menu: # if we're in the menu, we want to draw it and skip the rest of the loop
                self.menu.draw(self.virtual_screen)

                # SCALE TO WINDOW (same as draw())
                scale_x = self.WIDTH / SCREEN_WIDTH
                scale_y = self.HEIGHT / SCREEN_HEIGHT
                scale = min(scale_x, scale_y)

                offset_x = (self.WIDTH - SCREEN_WIDTH * scale) / 2
                offset_y = (self.HEIGHT - SCREEN_HEIGHT * scale) / 2

                scaled_surface = pygame.transform.scale(
                    self.virtual_screen,
                    (int(SCREEN_WIDTH * scale), int(SCREEN_HEIGHT * scale))
                )

                self.screen.fill((0,0,0))
                self.screen.blit(scaled_surface, (offset_x, offset_y))
                pygame.display.flip()
            else:
                if not self.paused:
                    while accumulator >= FIXED_DT:
                        self.update(inputs_per_player)  # <-- pass the inputs here! what the fuck did i mean here
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

    def draw_pause_overlay(self):
        font = pygame.font.SysFont(None, 48)
        text = font.render("PAUSED | ESC = Resume | Q = Menu", True, (255, 255, 255))
        self.screen.blit(text, (100, 100))
        pygame.display.flip()

    def handle_resize(self, new_width, new_height):
        self.WIDTH, self.HEIGHT = new_width, new_height
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.RESIZABLE)
    
    def reset_to_menu(self):
        self.in_menu = True
        self.paused = False

        # Recreate game state cleanly
        self.__init__()

    def draw(self):
        # 1. Draw everything to the virtual screen
        self.virtual_screen.blit(self.background, (0, 0))

        self.renderer.draw(self.virtual_screen)
        self.level.draw(self.virtual_screen)
        for i, render in enumerate(self.player_renders):
            render.draw(self.virtual_screen, self.player_sims[i])

        # 2. Compute scaling to fit the window while preserving aspect ratio
        scale_x = self.WIDTH / SCREEN_WIDTH
        scale_y = self.HEIGHT / SCREEN_HEIGHT
        scale = min(scale_x, scale_y)  # keep aspect ratio

        # Compute letterbox offsets
        offset_x = (self.WIDTH - SCREEN_WIDTH * scale) / 2
        offset_y = (self.HEIGHT - SCREEN_HEIGHT * scale) / 2

        # 3. Scale virtual screen to window
        scaled_surface = pygame.transform.scale(
            self.virtual_screen, 
            (int(SCREEN_WIDTH * scale), int(SCREEN_HEIGHT * scale))
        )

        # 4. Blit to real screen with letterbox offset
        self.screen.fill((0, 0, 0))  # black letterbox bars
        self.screen.blit(scaled_surface, (offset_x, offset_y))
        pygame.display.flip()

    def quit(self):
        pygame.quit()
        sys.exit()
