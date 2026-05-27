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

        # Map cards (in map select) — store data + thumbnail for each map
        self.map_cards = []

        # Logo
        self.logo = Logo()
        self.logo.animate_in()

        # Subtitle
        self.subtitle = Label("TAG • EVADE • SURVIVE", font_key="font_subtitle", color_key="secondary")
        self.subtitle.fade_in()

        # Main menu buttons
        self.main_buttons = [
            Button("START GAME"),
            Button("TUTORIAL"),
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
            self._build_map_cards()
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
        
        elif new_state == "TUTORIAL":
            self.state_title = Label("TUTORIAL", font_key="font_title", color_key="primary")
            self.state_title.fade_in()

    def _build_map_cards(self):
        from game.ui.map_card import MapCard
        import os
        from tools.path import resource_path

        self.map_cards = []
        for m in self.game.available_maps:
            folder = m["folder"]
            # Try loading preview, fall back to background, fall back to solid color
            surf = None
            for img_name in ["preview.png", "background.png"]:
                img_path = resource_path(os.path.join(folder, img_name))
                if os.path.exists(img_path):
                    try:
                        surf = pygame.image.load(img_path).convert()
                        break
                    except:
                        pass
            if surf is None:
                surf = pygame.Surface((340, 170))
                surf.fill(THEME["surface"])
            card = MapCard(m["name"], surf)
            # Lock if no map.tmj exists
            map_path = resource_path(os.path.join(folder, "map.tmj"))
            card.locked = not os.path.exists(map_path)
            card.fade_in()
            self.map_cards.append(card)

    def _get_card_positions(self):
        cols = 3
        pad_x = 60
        pad_y = 260        # ← was 160, now lower
        spacing_x = (SCREEN_WIDTH - pad_x * 2) // cols
        spacing_y = 280
        positions = []
        for i in range(len(self.map_cards)):
            col = i % cols
            row = i // cols
            cx = pad_x + spacing_x // 2 + col * spacing_x
            cy = pad_y + row * spacing_y
            positions.append((cx, cy))
        return positions

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
            return
        if event.type != pygame.KEYDOWN:
            return

        if self.state == "MAIN":
            self._handle_main(event.key)
        elif self.state == "TUTORIAL":
            if event.key == pygame.K_ESCAPE:
                self._transition_to("MAIN")
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
            self.game.sounds.play("menu_click")
        if key == pygame.K_DOWN:
            self.selection = (self.selection + 1) % count
            self._sync_selection()
            self.camera.shake(3)
            self.game.sounds.play("menu_click")
        if key == pygame.K_RETURN:
            self.game.sounds.play("menu_click")
            if self.selection == 0:
                from game.scenes.lobby_scene import LobbyScene
                self.game.replace_scene(LobbyScene(self.game))
            elif self.selection == 1:
                self._transition_to("TUTORIAL")
            elif self.selection == 2:
                self._transition_to("CUSTOM_SELECT")
            elif self.selection == 3:
                self.game.running = False

    def _handle_custom_select(self, key):
        if key in (pygame.K_UP, pygame.K_DOWN):
            self.player_to_edit = (self.player_to_edit + 1) % 2
            self._update_player_selection()
            self.camera.shake(3)
            self.game.sounds.play("menu_click")
        if key == pygame.K_RETURN:
            self._transition_to("CUSTOM_EDIT")
            self.game.sounds.play("menu_click")
        if key == pygame.K_ESCAPE:
            self._transition_to("MAIN")
            self.game.sounds.play("menu_click")

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
        count = len(self.game.available_maps)
        if key == pygame.K_LEFT:
            self.selected_map_idx = (self.selected_map_idx - 1) % count
            self.camera.shake(3)
        if key == pygame.K_RIGHT:
            self.selected_map_idx = (self.selected_map_idx + 1) % count
            self.camera.shake(3)
        if key == pygame.K_UP:
            self.selected_map_idx = (self.selected_map_idx - 3) % count
            self.camera.shake(3)
        if key == pygame.K_DOWN:
            self.selected_map_idx = (self.selected_map_idx + 3) % count
            self.camera.shake(3)        
        if key == pygame.K_RETURN:
            if self.map_cards[self.selected_map_idx].locked:
                self.camera.shake(8)  # nuhuh skake ahh blud
                return
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
        if self.state == "CUSTOM_SELECT": return self.player_buttons
        return []   # map cards update themselves in _draw_map_select

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
        elif self.state == "TUTORIAL":
            self._draw_tutorial(screen)

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
        self.state_title.draw(screen, SCREEN_WIDTH // 2, 40, anchor="midtop")

        positions = self._get_card_positions()
        for i, card in enumerate(self.map_cards):
            card.update(i == self.selected_map_idx)
            if i < len(positions):
                card.draw(screen, *positions[i])

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

    def _draw_tutorial(self, screen):
        self.state_title.draw(screen, SCREEN_WIDTH // 2, 40, anchor="midtop")

        font_header = pygame.font.SysFont("Arial", 24, bold=True)
        font_body   = pygame.font.SysFont("Arial", 22)

        lines = [
            ("GOAL", True),
            ("Don't be the tagger when your timer runs out. If your timer hits 0, you lose.", False),
            ("", False),
            ("HOW TO TAG", True),
            ("Walk into the other player while you are the tagger.", False),
            ("The yellow circle shows your tag range.", False),
            ("", False),
            ("CONTROLS", True),
            ("Player 1:   Move = S F     Jump = E     Ability = D", False),
            ("Player 2:   Move = ARROWS  Jump = UP    Ability = DOWN", False),
            ("", False),
            ("ABILITIES  (randomized on each tag, only usable as tagger)", True),
            ("LZR  Laser   >>  Fires a horizontal beam. Tags instantly if opponent is on same level.", False),
            ("SPD  Speed   >>  Boosts your movement speed for 4 seconds.", False),
            ("FRZ  Freeze  >>  Homing cube. Freezes the opponent for 3 seconds if it hits.", False),
            ("GLT  Glitch  >>  Homing cube. Tags the opponent if it hits.", False),
            ("", False),
            ("TIMER", True),
            ("Your timer only counts down while YOU are the tagger.", False),
            ("Ability cooldowns only regenerate while you are the runner.", False),
            ("", False),
            ("ONLINE", True),
            ("Enter a 4-letter room code to play online. Both players must use the same code.", False),
            ("Type OOOO for local splitscreen on the same keyboard.", False),
            ("", False),
            ("ESC   Back to menu", True),
        ]

        y = 120
        for text, is_header in lines:
            if not text:
                y += 14
                continue
            if is_header:
                surf = font_header.render(text, True, THEME["accent"])
            else:
                surf = font_body.render(text, True, (180, 180, 180))
            screen.blit(surf, (80, y))
            y += 30