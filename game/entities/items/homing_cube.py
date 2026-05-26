# game/entities/items/homing_cube.py
import pygame
from game.entities.items.base_item import BaseItem
from game.ui.animator import lerp

CUBE_SIZE = 20
CUBE_SPEED = 180      # pixels per second
CUBE_LIFETIME = 3.0   # seconds before it expires

class HomingCube(BaseItem):
    def __init__(self, effect: str):
        """effect = 'freeze' or 'glitch'"""
        self.effect = effect
        self.active = False
        self._lifetime = 0.0
        self._user_id = None
        self._target_id = None
        self._x = 0.0
        self._y = 0.0
        self._hit = False
        self._alpha = 255

    def on_use(self, app, user_id: int):
        sim = app.player_sims[user_id]
        self._user_id = user_id
        self._target_id = 1 - user_id
        self._x = float(sim.rect.centerx)
        self._y = float(sim.rect.centery)
        self._lifetime = CUBE_LIFETIME
        self._hit = False
        self.active = True

        sfx = "power_freeze" if self.effect == "freeze" else "power_glitch"
        app.sounds.play(sfx)

    def update(self, app):
        if not self.active:
            return

        dt = app.render_dt
        self._lifetime -= dt

        if self._lifetime <= 0:
            self.active = False
            return

        # Move toward target
        target_sim = app.player_sims[self._target_id]
        tx, ty = target_sim.rect.centerx, target_sim.rect.centery
        dx = tx - self._x
        dy = ty - self._y
        dist = max(1, (dx**2 + dy**2) ** 0.5)
        self._x += (dx / dist) * CUBE_SPEED * dt
        self._y += (dy / dist) * CUBE_SPEED * dt

        # Fade out in last 0.5s
        self._alpha = int(255 * min(1.0, self._lifetime / 0.5))

        # Hit check
        cube_rect = pygame.Rect(
            self._x - CUBE_SIZE // 2,
            self._y - CUBE_SIZE // 2,
            CUBE_SIZE, CUBE_SIZE
        )
        if cube_rect.colliderect(target_sim.rect):
            self._apply_effect(app)
            self.active = False

    def _apply_effect(self, app):
        user_sim   = app.player_sims[self._user_id]
        target_sim = app.player_sims[self._target_id]

        if self.effect == "freeze":
            target_sim.stun_timer = 180   # 3 seconds at 60hz
            target_sim.vel_x = 0
            target_sim.vel_y = 0

        elif self.effect == "glitch":
            # Tag the target
            user_sim.is_tagger   = False
            target_sim.is_tagger = True
            target_sim.stun_timer = 20
            user_sim.tagback_cooldown = user_sim.tagback_cooldown_time

    def draw(self, screen):
        if not self.active:
            return

        color = (100, 180, 255) if self.effect == "freeze" else (180, 100, 255)
        surf = pygame.Surface((CUBE_SIZE, CUBE_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(surf, (*color, self._alpha),
                         (0, 0, CUBE_SIZE, CUBE_SIZE),
                         border_radius=4)
        pygame.draw.rect(surf, (255, 255, 255, self._alpha),
                         (0, 0, CUBE_SIZE, CUBE_SIZE),
                         width=2, border_radius=4)
        screen.blit(surf, (self._x - CUBE_SIZE // 2, self._y - CUBE_SIZE // 2))