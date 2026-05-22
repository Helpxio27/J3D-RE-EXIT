# game/scenes/menu_scene.py
import pygame
import random
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from game.scenes.base_scene import BaseScene
from game.world.camera import Camera
from game.ui.widgets import Button, Label, Logo, LoadingBar
from game.ui.theme import THEME
import tkinter as tk
from tkinter import filedialog
from game.entities.particles.particle import ParticleEmitter
class MenuScene(BaseScene):
    def __init__(self, game):
        self.game = game

        self.state = "MAIN"
        self.selection = 0
        self.player_to_edit = 0
        self.selected_map_idx = 0

        # Camera for menu animations
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Background particles
        
        self.particles = ParticleEmitter()
        self._particle_timer = 0.0

        # Logo
        self.logo = Logo()
        self.logo.animate_in()

        # Subtitle
        self.subtitle = Label("TAG • EVADE • SURVIVE", font_key="font_subtitle", color_key="secondary")
        self.subtitle.fade_in()

        # Main menu buttons
        self.main_buttons = [
            Button("START GAME"),
            Button("CUSTOMIZE PLAYERS"),
            Button("EXIT", style="danger"),
        ]
        self._animate_buttons_in(self.main_buttons)
        self._sync_selection()

        # Map select button
        self.map_buttons = []

        # Player select buttons
        self.player_buttons = [
            Button("PLAYER 1"),
            Button("PLAYER 2"),
        ]

        # Hint label at bottom
        self.hint = Label("↑↓ Navigate   ENTER Select   ESC Back",
                          font_key="font_small", color_key="secondary")
        self.hint.fade_in()

        # State title label
        self.state_title = Label("", font_key="font_title", color_key="primary")

        # Transition overlay (for state changes)
        self._overlay_alpha = 0.0
        self._transitioning = False
        self._next_state = None

    # =====================
    # ANIMATION HELPERS
    # =====================
    def _animate_buttons_in(self, buttons, base_delay=0):
        for i, btn in enumerate(buttons):
            btn.slide_in_from_left(300 + i * 40)
            btn.fade_in()

    def _sync_selection(self):
        for i, btn in enumerate(self.main_buttons):
            btn.set_selected(i == self.selection)

    def _transition_to(self, new_state):
        """Triggers a fade-out → state change → fade-in"""
        self._transitioning = True
        self._next_state = new_state
        self._overlay_alpha = 0.0

    def _apply_state(self, new_state):
        self.state = new_state
        self.selection = 0

        if new_state == "MAIN":
            self._animate_buttons_in(self.main_buttons)
            self._sync_selection()
            self.logo.animate_in()

        elif new_state == "MAP_SELECT":
            self.map_buttons = [
                Button(m["name"]) for m in self.game.available_maps
            ]
            self._animate_buttons_in(self.map_buttons)
            self._update_map_selection()
            self.state_title = Label("SELECT MAP", font_key="font_title", color_key="primary")
            self.state_title.fade_in()

        elif new_state == "CUSTOM_SELECT":
            self._animate_buttons_in(self.player_buttons)
            self._update_player_selection()
            self.state_title = Label("SELECT PLAYER", font_key="font_title", color_key="primary")
            self.state_title.fade_in()

        elif new_state == "CUSTOM_EDIT":
            self.state_title = Label(
                f"EDITING PLAYER {self.player_to_edit + 1}",
                font_key="font_title", color_key="primary"
            )
            self.state_title.fade_in()

    def _update_map_selection(self):
        for i, btn in enumerate(self.map_buttons):
            btn.set_selected(i == self.selected_map_idx)

    def _update_player_selection(self):
        for i, btn in enumerate(self.player_buttons):
            btn.set_selected(i == self.player_to_edit)

    # =====================
    # EVENTS
    # =====================
    def handle_events(self, event):
        if self._transitioning:
            return  # block input during transition
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

    def _handle_main(self, key):
        count = len(self.main_buttons)
        if key == pygame.K_UP:
            self.selection = (self.selection - 1) % count
            self._sync_selection()
            self.camera.shake(3)
        if key == pygame.K_DOWN:
            self.selection = (self.selection + 1) % count
            self._sync_selection()
            self.camera.shake(3)
        if key == pygame.K_RETURN:
            if self.selection == 0:
                # Go to lobby instead of directly to map select
                from game.scenes.lobby_scene import LobbyScene
                self.game.replace_scene(LobbyScene(self.game))
            elif self.selection == 1: self._transition_to("CUSTOM_SELECT")
            elif self.selection == 2: self.game.running = False

    def _handle_custom_select(self, key):
        if key in (pygame.K_UP, pygame.K_DOWN):
            self.player_to_edit = (self.player_to_edit + 1) % 2
            self._update_player_selection()
            self.camera.shake(3)
        if key == pygame.K_RETURN:
            self._transition_to("CUSTOM_EDIT")
        if key == pygame.K_ESCAPE:
            self._transition_to("MAIN")

    def _handle_custom_edit(self, key):
        if key == pygame.K_i:
            self._load_custom_skin()
        if key == pygame.K_c:
            self.game.player_renders[self.player_to_edit].color = (
                random.randint(50, 255),
                random.randint(50, 255),
                random.randint(50, 255)
            )
            self.camera.shake(5)
        if key == pygame.K_ESCAPE:
            self._transition_to("CUSTOM_SELECT")

    def _handle_map_select(self, key):
        maps = self.game.available_maps
        if key == pygame.K_UP:
            self.selected_map_idx = (self.selected_map_idx - 1) % len(maps)
            self._update_map_selection()
            self.camera.shake(3)
        if key == pygame.K_DOWN:
            self.selected_map_idx = (self.selected_map_idx + 1) % len(maps)
            self._update_map_selection()
            self.camera.shake(3)
        if key == pygame.K_RETURN:
            self.camera.add_action("shake", 10)
            self.camera.add_action("zoom", 1.1, 0.15)
            self.camera.add_action("wait", 0.3)
            self.game.start_game(self.selected_map_idx)
        if key == pygame.K_ESCAPE:
            self._transition_to("MAIN")

    def _load_custom_skin(self):
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            title="Select a player skin",
            filetypes=[("Image files", "*.png *.jpg *.jpeg")]
        )
        root.destroy()
        if file_path:
            try:
                image = pygame.image.load(file_path).convert_alpha()
                self.game.player_renders[self.player_to_edit].custom_image = image
            except Exception as e:
                print(f"Failed to load skin: {e}")

    # =====================
    # UPDATE
    # =====================
    def update(self, accumulator):
        dt = self.game.render_dt

        # Update camera
        self.camera.update(dt)

        # Update logo + subtitle
        self.logo.update()
        self.subtitle.update()
        self.hint.update()
        self.state_title.update()

        # Update active buttons
        for btn in self._active_buttons():
            btn.update()

        # Background particles
        self._particle_timer += dt
        if self._particle_timer > 0.05:
            self._particle_timer = 0.0
            self.particles.emit(
                pos=(random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT + 10),
                vel=(random.uniform(-10, 10), random.uniform(-60, -30)),
                amount=1,
                spread=5,
                color=THEME["accent"],
                size=2,
                lifetime=4.0,
                alpha=60,
                fade_curve='ease-out'
            )
        self.particles.update(dt)

        # Transition overlay
        if self._transitioning:
            self._overlay_alpha += dt * 600  # fade to black
            if self._overlay_alpha >= 255:
                self._overlay_alpha = 255
                self._apply_state(self._next_state)
                self._transitioning = False
                self._next_state = None
        else:
            self._overlay_alpha = max(0.0, self._overlay_alpha - dt * 400)  # fade back in

        return accumulator

    def _active_buttons(self):
        if self.state == "MAIN":          return self.main_buttons
        if self.state == "MAP_SELECT":    return self.map_buttons
        if self.state == "CUSTOM_SELECT": return self.player_buttons
        return []

    # =====================
    # DRAW
    # =====================
    def draw(self, screen):
        # Background
        screen.fill(THEME["background"])

        # Background particles
        self.particles.draw(screen)

        if self.state == "MAIN":
            self._draw_main(screen)
        elif self.state == "MAP_SELECT":
            self._draw_map_select(screen)
        elif self.state == "CUSTOM_SELECT":
            self._draw_player_select(screen)
        elif self.state == "CUSTOM_EDIT":
            self._draw_player_edit(screen)

        # Hint at bottom
        self.hint.draw(screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50, anchor="midbottom")

        # Transition overlay
        if self._overlay_alpha > 0:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(int(self._overlay_alpha))
            screen.blit(overlay, (0, 0))

        # Apply camera
        result = self.camera.apply(screen)
        if result is not screen:
            screen.blit(result, (0, 0))

    def _draw_main(self, screen):
        # Logo
        self.logo.draw(screen, SCREEN_WIDTH // 2, 80, anchor="midtop")

        # Subtitle
        self.subtitle.draw(screen, SCREEN_WIDTH // 2, 220, anchor="midtop")

        # Buttons stacked on left
        for i, btn in enumerate(self.main_buttons):
            btn.draw(screen, 120, 360 + i * 100, anchor="midleft")

    def _draw_map_select(self, screen):
        self.state_title.draw(screen, SCREEN_WIDTH // 2, 80, anchor="midtop")

        for i, btn in enumerate(self.map_buttons):
            btn.draw(screen, 120, 280 + i * 90, anchor="midleft")

    def _draw_player_select(self, screen):
        self.state_title.draw(screen, SCREEN_WIDTH // 2, 80, anchor="midtop")

        for i, btn in enumerate(self.player_buttons):
            btn.draw(screen, 280, 320 + i * 150, anchor="midleft")
            # Player preview next to button
            preview_center = (180, 340 + i * 150)
            self.game.player_renders[i].draw_at(
                screen, self.game.player_sims[i], preview_center
            )

    def _draw_player_edit(self, screen):
        self.state_title.draw(screen, SCREEN_WIDTH // 2, 80, anchor="midtop")

        hint = Label("[I] Load Skin   [C] Random Color   ESC Back",
                     font_key="font_small", color_key="secondary")
        hint.alpha = 255
        hint.draw(screen, SCREEN_WIDTH // 2, 180, anchor="midtop")

        # Player preview centered
        preview_center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.game.player_renders[self.player_to_edit].draw_at(
            screen, self.game.player_sims[self.player_to_edit], preview_center
        )