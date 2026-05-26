# game/ui/hud.py
import pygame
from game.ui.theme import THEME
from game.ui.animator import lerp, lerp_color
from game.ui.widgets import get_font

CARD_W = 340
CARD_H = 80
CARD_RADIUS = 14
ABILITY_W = 52
ABILITY_H = 52
GAP = 40             # gap between the two cards
BOTTOM_MARGIN = 20   # distance from bottom of screen


class AbilitySlot:
    def __init__(self):
        self.ability_name = None
        self.cooldown = 0.0
        self._pulse = 0.0

    def update(self, dt):
        if self.cooldown <= 0:
            self._pulse = (self._pulse + dt * 3) % 1.0

    def draw(self, surf, x, y):
        pygame.draw.rect(surf, (15, 15, 15),
                         (x, y, ABILITY_W, ABILITY_H),
                         border_radius=8)

        font = get_font("font_small")
        if self.ability_name:
            short = {
                "laser":  "LZR",
                "speed":  "SPD",
                "freeze": "FRZ",
                "glitch": "GLT",
            }.get(self.ability_name, "???")
            txt = font.render(short, True, THEME["accent"])
            surf.blit(txt, txt.get_rect(center=(x + ABILITY_W // 2, y + ABILITY_H // 2 - 6)))

            # Cooldown fill overlay
            if self.cooldown > 0:
                overlay = pygame.Surface((ABILITY_W, ABILITY_H), pygame.SRCALPHA)
                fill_h = int(ABILITY_H * self.cooldown)
                overlay.fill((0, 0, 0, 160),
                             (0, ABILITY_H - fill_h, ABILITY_W, fill_h))
                surf.blit(overlay, (x, y))

            # Bottom cooldown bar
            bar_h = 4
            bar_y = y + ABILITY_H - bar_h - 2
            pygame.draw.rect(surf, THEME["border"],
                             (x + 4, bar_y, ABILITY_W - 8, bar_h),
                             border_radius=2)
            if self.cooldown < 1.0:
                fill_w = int((ABILITY_W - 8) * (1.0 - self.cooldown))
                pygame.draw.rect(surf, THEME["accent"],
                                 (x + 4, bar_y, fill_w, bar_h),
                                 border_radius=2)
        else:
            txt = font.render("?", True, (50, 50, 50))
            surf.blit(txt, txt.get_rect(center=(x + ABILITY_W // 2, y + ABILITY_H // 2)))

        # Border — pulses when ready
        if self.ability_name and self.cooldown <= 0:
            pulse = abs((self._pulse - 0.5) * 2)
            border = lerp_color(THEME["accent"], (160, 120, 0), pulse)
        else:
            border = (40, 40, 40)
        pygame.draw.rect(surf, border,
                         (x, y, ABILITY_W, ABILITY_H),
                         width=1, border_radius=8)


class PlayerCard:
    def __init__(self, player_id: int, color: tuple):
        self.player_id = player_id
        self.color = color
        self.ability_slot = AbilitySlot()
        self._tagger_t = 0.0
        self._alpha = 0.0

    def fade_in(self):
        self._alpha = 0.0

    def update(self, dt, sim, timer):
        self._alpha = lerp(self._alpha, 210, 0.08)
        self._tagger_t = lerp(self._tagger_t, 1.0 if sim.is_tagger else 0.0, 0.08)
        self.ability_slot.update(dt)
        if not sim.is_tagger and self.ability_slot.cooldown > 0:
            self.ability_slot.cooldown = max(0.0, self.ability_slot.cooldown - dt / 20.0)

    def draw(self, screen, cx, y, sim, timer):
        """Draw card centered at cx, bottom at y + CARD_H"""
        surf = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)

        # Card background — dark, slight color tint when tagger
        bg = lerp_color((10, 10, 10), self.color, self._tagger_t * 0.08)
        pygame.draw.rect(surf, (*bg, int(self._alpha)),
                         (0, 0, CARD_W, CARD_H),
                         border_radius=CARD_RADIUS)

        # Card border — accent when tagger
        border = lerp_color((35, 35, 35), THEME["accent"], self._tagger_t * 0.8)
        pygame.draw.rect(surf, (*border, int(self._alpha)),
                         (0, 0, CARD_W, CARD_H),
                         width=2, border_radius=CARD_RADIUS)

        pad = 14

        # Player color dot
        pygame.draw.circle(surf, self.color, (pad + 6, CARD_H // 2 - 8), 6)

        name_font = get_font("font_small")   # ← add this back
        name_text = f"PLAYER {self.player_id + 1}"
        name_surf = name_font.render(name_text, True, self.color)
        surf.blit(name_surf, (pad + 18, 14))

        if self._tagger_t > 0.05:
            tag_font = get_font("font_small")
            separator_surf = tag_font.render("  |  ", True, (60, 60, 60))
            tag_surf = tag_font.render("TAGGER", True, THEME["accent"])
            tag_surf.set_alpha(int(255 * self._tagger_t))
            sep_x = pad + 18 + name_surf.get_width()
            surf.blit(separator_surf, (sep_x, 14))
            surf.blit(tag_surf, (sep_x + separator_surf.get_width(), 14))
                
        # Timer text
        if timer:
            ratio = timer.time_left / timer.duration
            t_color = lerp_color((255, 70, 70), (200, 200, 200), ratio)
            timer_font = get_font("font_timer")
            t_surf = timer_font.render(timer.format(), True, t_color)
            # Centered vertically, after the name block
            t_rect = t_surf.get_rect(midleft=(pad + 18, CARD_H - 20))
            surf.blit(t_surf, t_rect)

            # Timer bar — thin line at very bottom of card
            bar_x = pad
            bar_y = CARD_H - 5
            bar_w = CARD_W - ABILITY_W - pad * 3 - 10
            bar_h = 3
            pygame.draw.rect(surf, (30, 30, 30),
                             (bar_x, bar_y, bar_w, bar_h),
                             border_radius=2)
            fill_w = int(bar_w * ratio)
            if fill_w > 0:
                pygame.draw.rect(surf, lerp_color((255, 60, 60), THEME["accent"], ratio),
                                 (bar_x, bar_y, fill_w, bar_h),
                                 border_radius=2)

        # Ability slot — right side, vertically centered
        self.ability_slot.draw(surf,
                               CARD_W - ABILITY_W - pad,
                               (CARD_H - ABILITY_H) // 2)

        surf.set_alpha(int(self._alpha))
        rect = surf.get_rect(midbottom=(cx, y))
        screen.blit(surf, rect)


class HUD:
    def __init__(self, player_colors: list):
        self.cards = [
            PlayerCard(i, player_colors[i])
            for i in range(len(player_colors))
        ]
        for c in self.cards:
            c.fade_in()

    def update(self, dt, player_sims, timer_system):
        for i, card in enumerate(self.cards):
            sim = player_sims[i] if i < len(player_sims) else None
            timer = timer_system.timers[i] if timer_system else None
            if sim:
                card.update(dt, sim, timer)

    def draw(self, screen, player_sims, timer_system, screen_w, screen_h):
        total_w = CARD_W * 2 + GAP
        start_cx = (screen_w - total_w) // 2 + CARD_W // 2
        card_y = screen_h - BOTTOM_MARGIN

        for i, card in enumerate(self.cards):
            sim = player_sims[i] if i < len(player_sims) else None
            timer = timer_system.timers[i] if timer_system else None
            if sim:
                cx = start_cx + i * (CARD_W + GAP)
                card.draw(screen, cx, card_y, sim, timer)