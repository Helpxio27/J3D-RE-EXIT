# game/entities/player/render.py
import pygame
from game.entities.particles.particle import ParticleEmitter

class PlayerRender:
    def __init__(self, color):
        self.color = color
        self.custom_image = None
        self.angle = 0
        self.trail = ParticleEmitter()

    def update(self, dt, sim):
        # Tilt based on horizontal velocity
        target_angle = max(-20, min(20, -sim.vel_x * 2.5))
        self.angle += (target_angle - self.angle) * 0.15

        # Particle trail
        speed = abs(sim.vel_x) + abs(sim.vel_y)
        if speed > 5:
            self.trail.emit(
                pos=sim.rect.center,
                vel=(0, 0),
                amount=3,
                spread=1.5,
                color=(255, 255, 255),
                size=4,
                lifetime=0.1,
                alpha=150,
                fade_curve='ease-out'
            )
        self.trail.update(dt)

    def draw(self, screen, sim):
        self.draw_at(screen, sim, sim.rect.center)

    def draw_at(self, screen, sim, center):
        """Draw at an arbitrary position — used for menu previews"""
        # Tag radius circle
        if sim.is_tagger:
            pygame.draw.circle(screen, (255, 255, 0), center, sim.tag_radius, 5)

        self.trail.draw(screen)

        if self.custom_image:
            rect = self.custom_image.get_rect(center=center)
            screen.blit(self.custom_image, rect)
        else:
            outline = 2
            surf = pygame.Surface((sim.rect.width + outline*2, sim.rect.height + outline*2), pygame.SRCALPHA)
            pygame.draw.rect(surf, (255, 255, 255), (0, 0, surf.get_width(), surf.get_height()), border_radius=6)
            pygame.draw.rect(surf, self.color, (outline, outline, sim.rect.width, sim.rect.height), border_radius=4)

            rotated = pygame.transform.rotate(surf, self.angle)
            rect = rotated.get_rect(center=center)
            screen.blit(rotated, rect.topleft)