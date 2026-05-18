# game/entities/particles.py
import pygame
import random
import math

class Particle:
    """Single particle"""
    _surface_cache = {}

    def __init__(self, pos, vel, lifetime, color, size, alpha=255, fade_curve='linear'):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(vel)
        self.lifetime = lifetime
        self.start_lifetime = lifetime
        self.color = color
        self.size = size
        self.alpha = alpha
        self.fade_curve = fade_curve

        key = (size, color)
        if key not in Particle._surface_cache:
            surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*color, 255), (size, size), size)
            Particle._surface_cache[key] = surf
        self.surf = Particle._surface_cache[key]

    def update(self, dt):
        self.lifetime -= dt
        self.pos += self.vel * dt
        
        life_ratio = max(self.lifetime / self.start_lifetime, 0)
        
        if self.fade_curve == 'linear':
            self.current_alpha = int(self.alpha * life_ratio)
        elif self.fade_curve == 'ease-out':
            self.current_alpha = int(self.alpha * math.sqrt(life_ratio))
        elif self.fade_curve == 'ease-in':
            self.current_alpha = int(self.alpha * (life_ratio ** 2))
        else:
            self.current_alpha = int(self.alpha * life_ratio) # Default Linear 

    def draw(self, surface, blend_mode=0):
        if self.lifetime <= 0:
            return
        temp_surf = self.surf.copy()
        temp_surf.fill((255, 255, 255, self.current_alpha), special_flags=pygame.BLEND_RGBA_MULT)
        surface.blit(temp_surf, (self.pos.x - self.size, self.pos.y - self.size), special_flags=blend_mode)


class ParticleEmitter:
    """Manages a pool of particles"""

    def __init__(self):
        self.particles = []

    def emit(self, pos, vel, amount=1, spread=0, color=(255,255,255), size=5, lifetime=1.0, alpha=255, fade_curve='linear'):
        vel = pygame.Vector2(vel)
        for _ in range(amount):
            rand_vel = pygame.Vector2(
                vel.x + random.uniform(-spread, spread),
                vel.y + random.uniform(-spread, spread)
            )
            self.particles.append(
                Particle(pos, rand_vel, lifetime, color, size, alpha, fade_curve)
            )

    def update(self, dt):
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.lifetime > 0]

    def draw(self, surface, blend_mode=0):
        for p in self.particles:
            p.draw(surface, blend_mode)