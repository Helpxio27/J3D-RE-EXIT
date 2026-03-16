import pygame
import random
from settings import SCREEN_WIDTH, SCREEN_HEIGHT
from level import Level
from level import MapRenderer

class Menu:
    def __init__(self, game):
        self.game = game

        self.state = "MAIN"
        self.selection = 0
        self.player_to_edit = 0
        self.selected_map_idx = 0

        self.font_title = pygame.font.SysFont("Arial", 60, bold=True)
        self.font_ui = pygame.font.SysFont("Arial", 40)

    def handle_events(self, event):
        if event.type != pygame.KEYDOWN:
            return

        # MAIN MENU
        if self.state == "MAIN":
            if event.key == pygame.K_UP:
                self.selection = (self.selection - 1) % 3
            if event.key == pygame.K_DOWN:
                self.selection = (self.selection + 1) % 3
            if event.key == pygame.K_RETURN:
                if self.selection == 0:
                    self.state = "MAP_SELECT"
                elif self.selection == 1:
                    self.state = "CUSTOM_SELECT"
                elif self.selection == 2:
                    self.game.running = False
        
        # PLAYER SELECT
        elif self.state == "CUSTOM_SELECT":

            if event.key in (pygame.K_UP, pygame.K_DOWN):
                self.player_to_edit = (self.player_to_edit + 1) % 2

            if event.key == pygame.K_RETURN:
                self.state = "CUSTOM_EDIT"

            if event.key == pygame.K_ESCAPE:
                self.state = "MAIN"

        # PLAYER EDIT
        elif self.state == "CUSTOM_EDIT":

            p = self.game.players[self.player_to_edit]

            if event.key == pygame.K_c:
                p.color = (
                    random.randint(50,255),
                    random.randint(50,255),
                    random.randint(50,255)
                )

            if event.key == pygame.K_ESCAPE:
                self.state = "CUSTOM_SELECT"

        # MAP SELECT
        elif self.state == "MAP_SELECT":
            maps = self.game.available_maps
            if event.key == pygame.K_UP:
                self.selected_map_idx = (self.selected_map_idx - 1) % len(maps)
            if event.key == pygame.K_DOWN:
                self.selected_map_idx = (self.selected_map_idx + 1) % len(maps)
            if event.key == pygame.K_RETURN:
                map_data = self.game.available_maps[self.selected_map_idx]
                self.game.level = Level(map_data["path"], map_data["tileset"])
                self.game.renderer = MapRenderer(self.game.level)
                self.game.reset_players_position()
                self.game.in_menu = False
            if event.key == pygame.K_ESCAPE:
                self.state = "MAIN"

    def draw(self, screen):
        screen.fill((20,20,20))
        if self.state == "MAIN":
            self.draw_main(screen)
        elif self.state == "CUSTOM_SELECT":
            self.draw_player_select(screen)
        elif self.state == "CUSTOM_EDIT":
            self.draw_player_edit(screen)
        elif self.state == "MAP_SELECT":
            self.draw_map_select(screen)

    def draw_main(self, screen):
        options = ["START GAME", "CUSTOMIZE PLAYERS", "EXIT"]
        for i,opt in enumerate(options):
            color = (255,255,0) if i == self.selection else (255,255,255)
            txt = self.font_ui.render(opt, True, color)
            screen.blit(txt, (100, 300 + i*80))

    def draw_map_select(self, screen):
        title = self.font_title.render("SELECT MAP", True, (255,255,255))
        screen.blit(title, (100,100))
        for i, m in enumerate(self.game.available_maps):
            color = (255,255,0) if i == self.selected_map_idx else (255,255,255)
            txt = self.font_ui.render(m["name"], True, color)
            screen.blit(txt, (150, 300 + i * 70))
    
    def draw_player_select(self, screen):
        title = self.font_title.render("SELECT PLAYER", True, (255,255,255))
        screen.blit(title, (100,100))
        for i in range(2):
            color = (255,255,0) if i == self.player_to_edit else (255,255,255)
            txt = self.font_ui.render(f"PLAYER {i+1}", True, color)
            screen.blit(txt, (250, 300 + i*150))
            # preview player
            p = self.game.players[i]
            preview_rect = pygame.Rect(0,0,30,30)
            preview_rect.center = (150, 320 + i*150)
            old_center = p.rect.center
            p.rect.center = preview_rect.center
            p.draw(screen)
            p.rect.center = old_center

    def draw_player_edit(self, screen):
        title = self.font_title.render(
            f"EDITING PLAYER {self.player_to_edit+1}",
            True,
            (255,255,255)
        )
        screen.blit(title, (100,50))
        info = self.font_ui.render(
            "[C] Random Color | ESC Back",
            True,
            (150,150,150)
        )
        screen.blit(info, (100,120))
        p = self.game.players[self.player_to_edit]
        old_center = p.rect.center
        p.rect.center = (
            self.game.WIDTH // 2,
            self.game.HEIGHT // 2
        )
        p.draw(screen)
        p.rect.center = old_center