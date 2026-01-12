import pygame
import random

class Particle:
    def __init__(self, pos, vel, lifetime, color, size):
        self.pos = pygame.Vector2(pos) # two var for position (x,y)
        self.vel = pygame.Vector2(vel) # two var for velocity (x,y)
        self.lifetime = lifetime # life time of particle in frames
        self.color = color # color of particle
        self.size = size # size (radius) of particle

    def update(self, dt):
        self.lifetime -= dt # decrease lifetime by delta time
        self.pos += self.vel * dt # update position based on velocity and delta time

    def draw(self, screen): # visual
        if self.lifetime > 0:
            pygame.draw.circle(screen, self.color, self.pos, self.size)

class ParticleEmitter: # box with alot of particles
    def __init__(self):
        self.particles = [] # list of particles

    def emit(self, pos, vel, amount, spread, color, size, lifetime):
        vel = pygame.Vector2(vel) # making vel a vector2
        
        for _ in range(amount): # create 'amount' of particles
            rand_vel = pygame.Vector2(
                vel.x + random.uniform(-spread, spread),
                vel.y + random.uniform(-spread, spread)
            ) # making random ass velocity value to be called in particle
            self.particles.append(
                Particle(pos, rand_vel, lifetime, color, size)
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