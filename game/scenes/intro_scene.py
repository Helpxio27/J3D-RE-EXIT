# game/scenes/intro_scene.py
import pygame
from game.scenes.base_scene import BaseScene
from game.ui.animator import lerp
from tools.path import resource_path
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT


class IntroScene(BaseScene):
    def __init__(self, app):
        self.app = app

        # Two logos in sequence
        self.logos = [
            resource_path("assets/ui/logo.png"),
            resource_path("assets/ui/bylogo.png"),
        ]
        self.current_idx = 0
        self._alpha = 0.0
        self._timer = 0.0
        self._phase = "fade_in"   # fade_in → hold → fade_out → next
        self._done = False

        self._load_current()

    def _load_current(self):
        try:
            img = pygame.image.load(self.logos[self.current_idx]).convert_alpha()
            # Scale to fit screen while keeping aspect ratio
            iw, ih = img.get_size()
            scale = min(SCREEN_WIDTH / iw, SCREEN_HEIGHT / ih) * 0.6
            self._logo = pygame.transform.scale(img, (int(iw * scale), int(ih * scale)))
        except Exception as e:
            print(f"[INTRO] Failed to load logo: {e}")
            self._logo = None

    def handle_events(self, event):
        if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            self._skip()

    def _skip(self):
        """Skip to next logo or straight to menu"""
        if self.current_idx < len(self.logos) - 1:
            self.current_idx += 1
            self._load_current()
            self._alpha = 0.0
            self._timer = 0.0
            self._phase = "fade_in"
        else:
            self._go_to_menu()

    def _go_to_menu(self):
        from game.scenes.menu_scene import MenuScene
        self.app.replace_scene(MenuScene(self.app))

    def update(self, accumulator):
        dt = self.app.render_dt

        if self._phase == "fade_in":
            self._alpha = lerp(self._alpha, 260, 0.04)
            if self._alpha >= 250:
                self._alpha = 255
                self._phase = "hold"
                self._timer = 0.0

        elif self._phase == "hold":
            self._timer += dt
            if self._timer >= 2.0:
                self._phase = "fade_out"

        elif self._phase == "fade_out":
            self._alpha = lerp(self._alpha, -10, 0.06)
            if self._alpha <= 0:
                self._alpha = 0
                if self.current_idx < len(self.logos) - 1:
                    self.current_idx += 1
                    self._load_current()
                    self._phase = "fade_in"
                else:
                    self._go_to_menu()

        return accumulator

    def draw(self, screen):
        screen.fill((0, 0, 0))
        if self._logo:
            self._logo.set_alpha(int(max(0, min(255, self._alpha))))
            rect = self._logo.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(self._logo, rect)