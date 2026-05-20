# game/scenes/menu_scene.py
import pygame
import random
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from game.world.level import Level, MapRenderer
import tkinter as tk
from tkinter import filedialog
from game.scenes.base_scene import BaseScene

class MenuScene(BaseScene):
    def __init__(self, game):
        self.game = game  # needs: available_maps, player_renders, start_game()

        self.state = "MAIN"
        self.selection = 0
        self.player_to_edit = 0
        self.selected_map_idx = 0

        self.font_title = pygame.font.SysFont("Arial", 60, bold=True)
        self.font_ui    = pygame.font.SysFont("Arial", 40)

    # ==========================================
    # DECIDES: which state transition to trigger
    # ==========================================
    def handle_events(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if self.state == "MAIN":
            self._handle_main(event.key)
        elif self.state == "CUSTOM_SELECT":
            self._handle_custom_select(event.key)
        elif self.state == "CUSTOM_EDIT":
            self._handle_custom_edit(event.key)
        elif self.state == "MAP_SELECT":
            self._handle_map_select(event.key)

    def _handle_main(self, key): # _ means it is used internally, convention python
        options_count = 3 # count modify box
        if key == pygame.K_UP:
            self.selection = (self.selection - 1) % options_count
        if key == pygame.K_DOWN:
            self.selection = (self.selection + 1) % options_count
        if key == pygame.K_RETURN:
            if self.selection == 0: self.state = "MAP_SELECT"
            elif self.selection == 1: self.state = "CUSTOM_SELECT"
            elif self.selection == 2: self.game.running = False

    def _handle_custom_select(self, key):
        if key in (pygame.K_UP, pygame.K_DOWN):
            self.player_to_edit = (self.player_to_edit + 1) % 2
        if key == pygame.K_RETURN:
            self.state = "CUSTOM_EDIT"
        if key == pygame.K_ESCAPE:
            self.state = "MAIN"

    def _handle_custom_edit(self, key):
        if key == pygame.K_i:
            self._load_custom_skin()
        if key == pygame.K_c:
            # DOES: randomizes the render color for this player
            self.game.player_renders[self.player_to_edit].color = (
                random.randint(50, 255),
                random.randint(50, 255),
                random.randint(50, 255)
            )
        if key == pygame.K_ESCAPE:
            self.state = "CUSTOM_SELECT"

    def _handle_map_select(self, key):
        maps = self.game.available_maps
        if key == pygame.K_UP:
            self.selected_map_idx = (self.selected_map_idx - 1) % len(maps)
        if key == pygame.K_DOWN:
            self.selected_map_idx = (self.selected_map_idx + 1) % len(maps)
        if key == pygame.K_RETURN:
            self.game.start_game(self.selected_map_idx)  # app.py decides what happens
        if key == pygame.K_ESCAPE:
            self.state = "MAIN"

    # ======================================================
    # DOES: opens file picker, loads skin onto player render
    # ======================================================
    def _load_custom_skin(self):
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            title="Select a player skin",
            filetypes=[("Image files", "*.png *.jpg *.jpeg")]
        )
        root.destroy()  # ← was missing in your original, causes a ghost window
        if file_path:
            try:
                image = pygame.image.load(file_path).convert_alpha()
                self.game.player_renders[self.player_to_edit].custom_image = image
            except Exception as e:
                print(f"Failed to load skin: {e}")

    # ==============================
    # DOES: draws current menu state
    # ==============================
    def draw(self, screen):
        screen.fill((20, 20, 20))
        if self.state == "MAIN":
            self._draw_main(screen)
        elif self.state == "CUSTOM_SELECT":
            self._draw_player_select(screen)
        elif self.state == "CUSTOM_EDIT":
            self._draw_player_edit(screen)
        elif self.state == "MAP_SELECT":
            self._draw_map_select(screen)

    def _draw_main(self, screen):
        options = ["START GAME", "CUSTOMIZE PLAYERS", "EXIT"]
        for i, opt in enumerate(options):
            color = (255, 255, 0) if i == self.selection else (255, 255, 255)
            screen.blit(self.font_ui.render(opt, True, color), (100, 300 + i * 80))

    def _draw_map_select(self, screen):
        screen.blit(self.font_title.render("SELECT MAP", True, (255, 255, 255)), (100, 100))
        for i, m in enumerate(self.game.available_maps):
            color = (255, 255, 0) if i == self.selected_map_idx else (255, 255, 255)
            screen.blit(self.font_ui.render(m["name"], True, color), (150, 300 + i * 70))

    def _draw_player_select(self, screen):
        screen.blit(self.font_title.render("SELECT PLAYER", True, (255, 255, 255)), (100, 100))
        for i in range(2):
            color = (255, 255, 0) if i == self.player_to_edit else (255, 255, 255)
            screen.blit(self.font_ui.render(f"PLAYER {i+1}", True, color), (250, 300 + i * 150))
            # preview: draw render at a fixed position without moving the real sim
            preview_center = (150, 320 + i * 150)
            self.game.player_renders[i].draw_at(screen, self.game.player_sims[i], preview_center)

    def _draw_player_edit(self, screen):
        screen.blit(self.font_title.render(
            f"EDITING PLAYER {self.player_to_edit + 1}", True, (255, 255, 255)), (100, 50))
        screen.blit(self.font_ui.render(
            "[I] Image  |  [C] Random Color  |  ESC Back", True, (150, 150, 150)), (100, 120))
        # preview player centered on screen
        preview_center = (self.game.WIDTH // 2, self.game.HEIGHT // 2)
        self.game.player_renders[self.player_to_edit].draw_at(
            screen, self.game.player_sims[self.player_to_edit], preview_center
        )

    # ==============================
    # Small update helper
    # ==============================
    def update(self, accumulator):
        return accumulator  # menu doesn't tick, just pass it through