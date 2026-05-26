# game/app.py
import json
import pygame
import sys
from config.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    FIXED_DT, RENDER_FPS, BACKGROUND_COLOR
)
from tools.path import resource_path
from game.world.level import Level, MapRenderer
from game.entities.player.sim import PlayerSim
from game.entities.player.render import PlayerRender
from game.scenes.menu_scene import MenuScene
import socket
import os, json
from tools.path import resource_path

class App:
    def __init__(self):
        pygame.init()

        # Window
        self.WIDTH, self.HEIGHT = SCREEN_WIDTH, SCREEN_HEIGHT
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        self.virtual_screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("RE-EXIT")
        self.clock = pygame.time.Clock()
        self.running = True

        # Network
        self.online = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(False)
        self.server_addr = ("localhost", 9999)

        # Maps 
        def _discover_maps(self): # Weird shit 
            folders = [
                "assets/maps/lv1",
                "assets/maps/lv2", 
                "assets/maps/lv3",
                "assets/maps/lv4",
                "assets/maps/lv5",
                "assets/maps/lv6",
            ]
            maps = []
            for folder in folders:
                cfg_path = resource_path(os.path.join(folder, "config.json"))
                if os.path.exists(cfg_path):
                    with open(cfg_path) as f:
                        cfg = json.load(f)
                    maps.append({
                        "name":   cfg.get("name", os.path.basename(folder).upper()),
                        "folder": folder
                    })
                else:
                    maps.append({
                        "name":   "COMING SOON",
                        "folder": folder
                    })
            return maps
        
        self.available_maps = _discover_maps(self)

        # Players
        # Loading configs
        from config.constants import PLAYER_1_COLOR, PLAYER_2_COLOR, SPAWN_POINTS
        from config.controls import CONTROLS

        self.spawn_points = list(SPAWN_POINTS)
        self.player_sims = [
            PlayerSim(self.spawn_points[0][0], self.spawn_points[0][1], is_tagger=True),
            PlayerSim(self.spawn_points[1][0], self.spawn_points[1][1], is_tagger=False),
        ]
        self.player_renders = [
            PlayerRender(PLAYER_1_COLOR),
            PlayerRender(PLAYER_2_COLOR),
        ]
        self.controls = CONTROLS


        # Background fallback
        try:
            self.background = pygame.transform.scale(
                pygame.image.load(resource_path("assets/maps/lv1/background.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT)
            )
        except:
            self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.background.fill(BACKGROUND_COLOR)

        self.level = None
        self.renderer = None

        # FPS counter
        self.fps_timer = 0.0
        self.fps_frames = 0
        self.render_dt = 0.0

        # ---- Scene stack ----
        # The top of the stack is always the active scene
        self.scene_stack = [MenuScene(self)]

        from game.systems.sound_system import SoundSystem
        self.sounds = SoundSystem()

        self.sounds.load("tag",          "assets/audio/sfx/tag.mp3")
        self.sounds.load("menu_click",   "assets/audio/sfx/menu_click.mp3")
        self.sounds.load("power_laser",  "assets/audio/sfx/power_laser.mp3")
        self.sounds.load("power_speed",  "assets/audio/sfx/power_speed.mp3")
        self.sounds.load("power_freeze", "assets/audio/sfx/power_freeze.mp3")
        self.sounds.load("power_glitch", "assets/audio/sfx/power_glitch.mp3")

        # Menu music starts immediately
        self.sounds.play_music("assets/audio/music/menu.mp3")

    # =====================
    # Scene stack helpers
    # =====================
    def push_scene(self, scene):
        """DOES: puts a new scene on top — old scene is paused underneath"""
        self.scene_stack.append(scene)

    def pop_scene(self):
        """DOES: removes top scene — resumes whatever was under it"""
        if len(self.scene_stack) > 1:
            self.scene_stack.pop()

    def replace_scene(self, scene):
        """DOES: swaps current scene — no going back"""
        self.scene_stack[-1] = scene

    @property
    def current_scene(self):
        """DECIDES: what's active right now"""
        return self.scene_stack[-1]

    # =====================
    # DOES: called by menu when player picks a map
    # =====================

    def _reset_players(self):
        from config.constants import MAX_SPEED
        for i, sim in enumerate(self.player_sims):
            sim.rect.center = self.spawn_points[i]
            sim.vel_x = 0
            sim.vel_y = 0
            sim.max_speed = MAX_SPEED  # ← reset speed to default
            sim.stun_timer = 0
            sim.tagback_cooldown = 0
            sim.power = None
            sim.power_ready = True

    def start_game(self, map_idx):
        from game.scenes.gameplay_scene import GameplayScene
        import os
        m = self.available_maps[map_idx]
        self.level = Level(m["folder"])
        self.renderer = MapRenderer(self.level)

        # Load background from this map's folder
        try:
            bg_path = resource_path(os.path.join(m["folder"], self.level.config.get("background", "background.png")))
            self.background = pygame.transform.scale(
                pygame.image.load(bg_path).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT)
            )
        except:
            self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.background.fill(BACKGROUND_COLOR)

        self._reset_players()
        self.online = False if not hasattr(self, 'client') or not self.client else self.online
        self.replace_scene(GameplayScene(self))

    # =====================
    # DOES: returns to menu cleanly
    # =====================
    def reset_to_menu(self):
        from game.scenes.menu_scene import MenuScene
        self.level = None
        self.renderer = None
        self._reset_players()
        self.replace_scene(MenuScene(self))      # swap gameplay for menu

    def _reset_players(self):
        for i, sim in enumerate(self.player_sims):
            sim.rect.center = self.spawn_points[i]
            sim.vel_x = 0
            sim.vel_y = 0

    # =====================
    # DOES: scales virtual screen to real window
    # =====================
    def _blit_scaled(self):
        scale = min(self.WIDTH / SCREEN_WIDTH, self.HEIGHT / SCREEN_HEIGHT)
        offset_x = (self.WIDTH  - SCREEN_WIDTH  * scale) / 2
        offset_y = (self.HEIGHT - SCREEN_HEIGHT * scale) / 2
        scaled = pygame.transform.scale(
            self.virtual_screen,
            (int(SCREEN_WIDTH * scale), int(SCREEN_HEIGHT * scale))
        )
        self.screen.fill((0, 0, 0))
        self.screen.blit(scaled, (offset_x, offset_y))

    def _handle_resize(self, w, h):
        self.WIDTH, self.HEIGHT = w, h
        self.screen = pygame.display.set_mode((w, h), pygame.RESIZABLE)

    def _build_inputs(self):
        keys = pygame.key.get_pressed()
        return [
            {
                "left":      keys[ctrl["left"]],
                "right":     keys[ctrl["right"]],
                "jump":      keys[ctrl["jump"]],
                "drop":      keys[ctrl["drop"]],
                "use_power": keys[ctrl["use_power"]],
            }
            for ctrl in self.controls
        ]

    def _send_network_input(self, input_dict: dict):
        if hasattr(self, 'client'):
            self.client.send_input(input_dict)

    # =====================
    # DOES: the main loop — now just delegates to current scene
    # =====================

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
            # Events go to current scene
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.VIDEORESIZE:
                    self._handle_resize(event.w, event.h)
                self.current_scene.handle_events(event)
            # Update + draw current scene
            accumulator = self.current_scene.update(accumulator)
            self.current_scene.draw(self.virtual_screen)
            self._blit_scaled()
            pygame.display.flip()
            # FPS counter
            self.fps_timer += frame_time
            self.fps_frames += 1
            if self.fps_timer >= 1.0:
                print(f"FPS: {self.fps_frames}")
                self.fps_timer -= 1.0
                self.fps_frames = 0
            self.clock.tick(RENDER_FPS)

        pygame.quit()
        sys.exit()