import pygame
import random

class Particle:
    def __init__(self, pos, vel, lifetime, color, size, alpha=255):
        self.pos = pygame.Vector2(pos) # two var for position (x,y)
        self.vel = pygame.Vector2(vel) # two var for velocity (x,y)
        self.lifetime = lifetime # life time of particle in frames
        self.start_lifetime = lifetime # Starting of the lifetime
        self.color = color # color of particle
        self.alpha = alpha # Fading coloring (0-255)
        self.size = size # size (radius) of particle
        self.current_alpha = alpha # Current alpha changing with lifetime

    def update(self, dt):
        self.lifetime -= dt # decrease lifetime by delta time
        self.pos += self.vel * dt # update position based on velocity and delta time

        # Linear alpha fade-out
        life_ratio = max(self.lifetime / self.start_lifetime, 0)
        self.current_alpha = int(self.alpha * life_ratio)

    def draw(self, surface):
        if self.lifetime <= 0:
            return

        # Create per-particle surface
        diameter = self.size * 2
        particle_surf = pygame.Surface((diameter, diameter), pygame.SRCALPHA)

        pygame.draw.circle(
            particle_surf,
            (*self.color, self.current_alpha),
            (self.size, self.size),
            self.size
        )

        surface.blit(
            particle_surf,
            (self.pos.x - self.size, self.pos.y - self.size)
        )


class ParticleEmitter: # box with alot of particles
    def __init__(self):
        self.particles = [] # list of particles

    def emit(self, pos, vel, amount, spread, color, size, lifetime, alpha=255):
        vel = pygame.Vector2(vel) # making vel a vector2
        
        for _ in range(amount): # create 'amount' of particles
            rand_vel = pygame.Vector2(
                vel.x + random.uniform(-spread, spread),
                vel.y + random.uniform(-spread, spread)
            ) # making random ass velocity value to be called in particle
            self.particles.append(
                Particle(pos, rand_vel, lifetime, color, size, alpha)
            ) # puts particle in list of particles managed

    def update(self, dt):
        for p in self.particles[:]:
            p.update(dt)
            if p.lifetime <= 0:
                self.particles.remove(p)

    def draw(self, screen):
        for p in self.particles:
            p.draw(screen)


# for _ in range(amount):
# the _ is just a naming convention telling us that we don't care about the variable