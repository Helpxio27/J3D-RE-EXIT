# logic/player_render.py
import pygame
from particles import ParticleEmitter

class PlayerRender:
    def __init__(self, color):
        self.color = color
        self.angle = 0
        self.trail = ParticleEmitter()

    def update(self, dt, sim):
        # Tilt angle based on horizontal velocity
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
        # Draw tag radius
        if sim.is_tagger:
            pygame.draw.circle(screen, (255, 255, 0), sim.rect.center, sim.tag_radius, 5)

        self.trail.draw(screen)

        # Draw player rectangle with outline
        outline = 2
        surf = pygame.Surface((sim.rect.width + outline*2, sim.rect.height + outline*2), pygame.SRCALPHA)
        pygame.draw.rect(surf, (255, 255, 255), (0, 0, surf.get_width(), surf.get_height()), border_radius=6)
        pygame.draw.rect(surf, self.color, (outline, outline, sim.rect.width, sim.rect.height), border_radius=4)

        rotated = pygame.transform.rotate(surf, self.angle)
        rect = rotated.get_rect(center=sim.rect.center)
        screen.blit(rotated, rect.topleft)