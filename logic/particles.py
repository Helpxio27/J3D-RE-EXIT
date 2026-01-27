import pygame
import random
import math

class Particle:
    """Single particle"""
    _surface_cache = {}  # cache for particle surfaces by (size, color)

    def __init__(self, pos, vel, lifetime, color, size, alpha=255, fade_curve='linear'):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(vel)
        self.lifetime = lifetime
        self.start_lifetime = lifetime
        self.color = color
        self.size = size
        self.alpha = alpha
        self.fade_curve = fade_curve

        # Pre-rendered surface from cache
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

        # fade curve
        if self.fade_curve == 'linear':
            self.current_alpha = int(self.alpha * life_ratio)
        elif self.fade_curve == 'ease-out':
            self.current_alpha = int(self.alpha * math.sqrt(life_ratio))
        elif self.fade_curve == 'ease-in':
            self.current_alpha = int(self.alpha * (life_ratio ** 2))
        else:
            self.current_alpha = int(self.alpha * life_ratio)

    def draw(self, surface, blend_mode=0):
        if self.lifetime <= 0:
            return

        # blit the cached surface with alpha
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
        # fast removal of dead particles
        self.particles = [p for p in self.particles if p.lifetime > 0]

    def draw(self, surface, blend_mode=0):
        for p in self.particles:
            p.draw(surface, blend_mode)


# class Particle:
#     def __init__(self, pos, vel, lifetime, color, size, alpha=255):
#         self.pos = pygame.Vector2(pos) # two var for position (x,y)
#         self.vel = pygame.Vector2(vel) # two var for velocity (x,y)
#         self.lifetime = lifetime # life time of particle in frames
#         self.start_lifetime = lifetime # Starting of the lifetime
#         self.color = color # color of particle
#         self.alpha = alpha # Fading coloring (0-255)
#         self.size = size # size (radius) of particle
#         self.current_alpha = alpha # Current alpha changing with lifetime

#     def update(self, dt):
#         self.lifetime -= dt # decrease lifetime by delta time
#         self.pos += self.vel * dt # update position based on velocity and delta time

#         # Linear alpha fade-out
#         life_ratio = max(self.lifetime / self.start_lifetime, 0)
#         self.current_alpha = int(self.alpha * life_ratio)

#     def draw(self, surface):
#         if self.lifetime <= 0:
#             return

#         # Create per-particle surface
#         diameter = self.size * 2
#         particle_surf = pygame.Surface((diameter, diameter), pygame.SRCALPHA)

#         pygame.draw.circle(
#             particle_surf,
#             (*self.color, self.current_alpha),
#             (self.size, self.size),
#             self.size
#         )

#         surface.blit(
#             particle_surf,
#             (self.pos.x - self.size, self.pos.y - self.size)
#         )


# class ParticleEmitter: # box with alot of particles
#     def __init__(self):
#         self.particles = [] # list of particles

#     def emit(self, pos, vel, amount, spread, color, size, lifetime, alpha=255):
#         vel = pygame.Vector2(vel) # making vel a vector2
        
#         for _ in range(amount): # create 'amount' of particles
#             rand_vel = pygame.Vector2(
#                 vel.x + random.uniform(-spread, spread),
#                 vel.y + random.uniform(-spread, spread)
#             ) # making random ass velocity value to be called in particle
#             self.particles.append(
#                 Particle(pos, rand_vel, lifetime, color, size, alpha)
#             ) # puts particle in list of particles managed

#     def update(self, dt):
#         for p in self.particles[:]:
#             p.update(dt)
#             if p.lifetime <= 0:
#                 self.particles.remove(p)

#     def draw(self, screen):
#         for p in self.particles:
#             p.draw(screen)


# for _ in range(amount):
# the _ is just a naming convention telling us that we don't care about the variable