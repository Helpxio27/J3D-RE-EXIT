# game/entities/items/laser.py
import pygame
from game.entities.items.base_item import BaseItem
from game.ui.animator import lerp

LASER_DURATION = 0.4   # seconds the beam stays visible
LASER_WIDTH = 12

class Laser(BaseItem):
    def __init__(self):
        self.active = False
        self._timer = 0.0
        self._user_id = None
        self._start = (0, 0)
        self._end = (0, 0)
        self._alpha = 0

    def on_use(self, app, user_id: int):
        sim = app.player_sims[user_id]
        self._user_id = user_id
        self._timer = LASER_DURATION
        self.active = True
        self._alpha = 255

        # Laser fires horizontally in the direction the player is facing
        direction = 1 if sim.vel_x >= 0 else -1
        cx, cy = sim.rect.center
        self._start = (cx, cy)
        self._end   = (cx + direction * 2000, cy)

        # Check if other player is hit
        other_id = 1 - user_id
        other_sim = app.player_sims[other_id]
        if self._laser_hits(other_sim.rect):
            # Tag them
            sim.is_tagger = False
            other_sim.is_tagger = True
            other_sim.stun_timer = 20
            sim.tagback_cooldown = sim.tagback_cooldown_time
        app.sounds.play("power_laser")

    def _laser_hits(self, rect: pygame.Rect) -> bool:
        """DECIDES: does the laser line intersect the rect"""
        laser_rect = pygame.Rect(
            min(self._start[0], self._end[0]),
            self._start[1] - LASER_WIDTH // 2,
            abs(self._end[0] - self._start[0]),
            LASER_WIDTH
        )
        return laser_rect.colliderect(rect)

    def update(self, app):
        if not self.active:
            return
        self._timer -= app.render_dt
        self._alpha = max(0, int(255 * (self._timer / LASER_DURATION)))
        if self._timer <= 0:
            self.active = False

    def draw(self, screen):
        if not self.active or self._alpha <= 0:
            return
        surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        color = (255, 50, 50, self._alpha)
        pygame.draw.line(surf, color, self._start, self._end, LASER_WIDTH)
        # Bright core
        pygame.draw.line(surf, (255, 255, 255, self._alpha),
                         self._start, self._end, 3)
        screen.blit(surf, (0, 0))