# game/ui/map_card.py
import pygame
from game.ui.theme import THEME
from game.ui.animator import lerp, lerp_color

CARD_W = 340
CARD_H = 240
PREVIEW_H = 170
RADIUS = 12

class MapCard:
    def __init__(self, name: str, preview_surf: pygame.Surface):
        self.name = name
        self.preview = pygame.transform.scale(preview_surf, (CARD_W - 4, PREVIEW_H))

        self._selected_t = 0.0   # 0 = default, 1 = selected
        self.alpha = 0
        self.target_alpha = 255
        self.scale = 0.92
        self.target_scale = 1.0

        self.locked = False

    def set_selected(self, selected: bool):
        self.target_scale = 1.04 if selected else 1.0

    def fade_in(self):
        self.alpha = 0
        self.target_alpha = 255
        self.scale = 0.88
        self.target_scale = 1.0

    def update(self, selected: bool):
        target_t = 1.0 if selected else 0.0
        self._selected_t = lerp(self._selected_t, target_t, THEME["lerp_speed_fast"])
        self.alpha = lerp(self.alpha, self.target_alpha, THEME["lerp_speed"])
        self.scale = lerp(self.scale, self.target_scale, THEME["lerp_speed_fast"])
        self.set_selected(selected)


    def draw(self, screen, cx, cy):
        w = int(CARD_W * self.scale)
        h = int(CARD_H * self.scale)
        prev_h = int(PREVIEW_H * self.scale)

        surf = pygame.Surface((w, h), pygame.SRCALPHA)

        # Background
        bg_color = lerp_color(THEME["surface"], THEME["btn_color_selected"], self._selected_t * 0.15)
        pygame.draw.rect(surf, (*bg_color, int(self.alpha)),
                        (0, 0, w, h), border_radius=RADIUS)

        # Preview image
        preview_scaled = pygame.transform.scale(self.preview, (w - 4, prev_h))
        preview_rect = preview_scaled.get_rect(midtop=(w // 2, 2))
        surf.blit(preview_scaled, preview_rect)

        # Name text
        from game.ui.widgets import get_font
        font = get_font("font_small")
        name_color = lerp_color(THEME["primary"], THEME["accent"], self._selected_t)
        name_surf = font.render(self.name.upper(), True, name_color)
        name_rect = name_surf.get_rect(center=(w // 2, prev_h + (h - prev_h) // 2))
        surf.blit(name_surf, name_rect)

        # Border
        border_color = lerp_color(THEME["border"], THEME["accent"], self._selected_t)
        border_width = int(lerp(1, 3, self._selected_t))
        pygame.draw.rect(surf, (*border_color, int(self.alpha)),
                        (0, 0, w, h),
                        width=border_width,
                        border_radius=RADIUS)

        # Lock overlay — drawn last so it's on top of everything
        if self.locked:
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            surf.blit(overlay, (0, 0))
            lock_font = get_font("font_ui")
            lock_surf = lock_font.render("SOON", True, (150, 150, 150))
            lock_rect = lock_surf.get_rect(center=(w // 2, h // 2))
            surf.blit(lock_surf, lock_rect)

        surf.set_alpha(int(self.alpha))
        rect = surf.get_rect(center=(cx, cy))
        screen.blit(surf, rect)