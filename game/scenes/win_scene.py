# game/scenes/win_scene.py
import pygame
from game.scenes.base_scene import BaseScene
from game.ui.widgets import Label, Logo
from game.ui.theme import THEME
from game.ui.animator import lerp
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from tools.path import resource_path

class WinScene(BaseScene):
    def __init__(self, app, winner_id: int, winner_color: tuple):
        self.app = app
        self.winner_id = winner_id
        self.winner_color = winner_color

        self._alpha = 0.0
        self._scale = 0.6
        self._timer = 0.0
        self._done = False

        # Labels
        self.winner_label = Label(
            f"PLAYER {winner_id + 1} WINS",
            font_key="font_title",
            color_key="accent"
        )
        self.sub_label = Label(
            "Returning to menu...",
            font_key="font_subtitle",
            color_key="secondary"
        )

        # Freeze the last frame as background
        self.frozen_frame = app.virtual_screen.copy()

    def handle_events(self, event):
        # Skip animation on any key
        if event.type == pygame.KEYDOWN:
            self._finish()

    def update(self, accumulator):
        dt = self.app.render_dt
        self._timer += dt

        self._alpha = lerp(self._alpha, 255, 0.06)
        self._scale = lerp(self._scale, 1.0, 0.08)

        if self._timer >= 15.0 and not self._done:
            self._finish()

        return accumulator

    def _finish(self):
        if self._done:
            return
        self._done = True
        self.app.sounds.fade_out_music(1500)
        self.app.sounds.play_music_after_fade(
            resource_path("assets/audio/music/menu.mp3"),
            delay_ms=1500
        )
        self.app.online = False
        self.app.client = None
        from game.scenes.menu_scene import MenuScene
        self.app.replace_scene(MenuScene(self.app))

    def draw(self, screen):
        # Frozen game world behind overlay
        screen.blit(self.frozen_frame, (0, 0))

        # Dark overlay fades in
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, int(self._alpha * 0.75)))
        screen.blit(overlay, (0, 0))

        # Winner card — scales in from center
        card_w = 600
        card_h = 220
        card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)

        # Card background
        pygame.draw.rect(card_surf, (10, 10, 10, int(self._alpha)),
                         (0, 0, card_w, card_h), border_radius=20)
        pygame.draw.rect(card_surf, (*self.winner_color, int(self._alpha)),
                         (0, 0, card_w, card_h), width=3, border_radius=20)

        # Winner text
        from game.ui.widgets import get_font
        title_font = get_font("font_title")
        sub_font   = get_font("font_subtitle")

        title_surf = title_font.render(f"PLAYER {self.winner_id + 1} WINS", True, self.winner_color)
        sub_surf   = sub_font.render("Returning to menu...", True, THEME["secondary"])

        card_surf.blit(title_surf, title_surf.get_rect(center=(card_w // 2, card_h // 2 - 30)))
        card_surf.blit(sub_surf,   sub_surf.get_rect(center=(card_w // 2, card_h // 2 + 50)))

        # Scale animation
        scaled_w = int(card_w * self._scale)
        scaled_h = int(card_h * self._scale)
        scaled = pygame.transform.scale(card_surf, (scaled_w, scaled_h))
        scaled.set_alpha(int(self._alpha))
        screen.blit(scaled, scaled.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))