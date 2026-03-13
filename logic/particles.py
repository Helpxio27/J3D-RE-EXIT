import pygame
import random
import math

class Particle:
    """Individual particle with size shrinking and alpha fading effects"""
    _surface_cache = {}  

    def __init__(self, pos, vel, lifetime, color, size, alpha=255, fade_curve='linear'):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(vel)
        self.lifetime = lifetime
        self.start_lifetime = lifetime
        self.color = color
        self.start_size = size
        self.alpha = alpha
        self.fade_curve = fade_curve
        self.current_size = size

    def update(self, dt):
        self.lifetime -= dt
        self.pos += self.vel * dt

        # Calculate life ratio (from 1.0 down to 0.0)
        life_ratio = max(self.lifetime / self.start_lifetime, 0)

        # 1. SIZE REDUCTION (Dissipation effect)
        self.current_size = self.start_size * life_ratio

        # 2. FADE CURVE (Alpha transparency)
        if self.fade_curve == 'linear':
            self.current_alpha = int(self.alpha * life_ratio)
        elif self.fade_curve == 'ease-out':
            self.current_alpha = int(self.alpha * math.sqrt(life_ratio))
        elif self.fade_curve == 'ease-in':
            self.current_alpha = int(self.alpha * (life_ratio ** 2))
        else:
            self.current_alpha = int(self.alpha * life_ratio)

    def draw(self, surface, blend_mode=0):
        if self.lifetime <= 0 or self.current_size < 0.5:
            return

        # Draw circle directly (smoother for dynamic resizing)
        s = int(self.current_size)
        if s < 1: s = 1
        
        # Draw the vaporous particle
        pygame.draw.circle(
            surface, 
            (*self.color, self.current_alpha), 
            (int(self.pos.x), int(self.pos.y)), 
            s
        )

class ParticleEmitter:
    """Optimized particle manager"""
    def __init__(self):
        self.particles = []

    def emit(self, pos, vel, amount=1, spread=0, color=(255,255,255), size=5, lifetime=1.0, alpha=255, fade_curve='linear'):
        vel = pygame.Vector2(vel)
        for _ in range(amount):
            # Add random spread to the direction
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
        # Remove dead particles
        self.particles = [p for p in self.particles if p.lifetime > 0]

    def draw(self, surface, blend_mode=0):
        for p in self.particles:
            p.draw(surface, blend_mode)

# --- PLAYER CLASSES FOR DYNAMIC VISUALS ---

class Player:
    def __init__(self, x, y, color=(255, 70, 70)):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.vel = pygame.Vector2(0, 0)
        self.on_ground = False
        self.speed = 5
        self.jump_force = -15
        
        # Personalization
        self.color = color
        self.custom_image = None
        self.angle = 0  # For the Tilt effect
        self.is_tagger = False
        self.tag_radius = 35

    def jump(self, emitter):
        """Triggers a jump with a vaporous smoke explosion"""
        if self.on_ground:
            self.vel.y = self.jump_force
            self.on_ground = False
            
            # --- IMPROVED SMOKE EFFECT ---
            if emitter:
                for _ in range(15):  # Particle count
                    # Upward and outward explosion
                    vx = random.uniform(-4, 4)
                    vy = random.uniform(-1, 2)
                    emitter.emit(
                        pos=(self.rect.centerx, self.rect.bottom),
                        vel=(vx, vy),
                        amount=1, 
                        spread=1, 
                        color=(220, 220, 220), 
                        size=random.randint(4, 10), # Large particles that shrink
                        lifetime=random.uniform(0.4, 0.8),
                        alpha=180,
                        fade_curve='ease-out'
                    )

    def update_animation(self, vel_x):
        """Tilts the cube and handles visual effects"""
        # Tilt: The cube leans based on horizontal velocity
        target_angle = -vel_x * 2.5
        self.angle += (target_angle - self.angle) * 0.15

    def draw(self, screen):
        # 1. Tagger Halo (Luminous Pulsation)
        if self.is_tagger:
            time = pygame.time.get_ticks() * 0.01
            pulse = abs(math.sin(time)) * 6
            pygame.draw.circle(screen, (255, 255, 0), self.rect.center, self.tag_radius + pulse, 3)

        # 2. Prepare the cube surface
        surf = pygame.Surface((40, 40), pygame.SRCALPHA)
        if self.custom_image:
            img_scaled = pygame.transform.scale(self.custom_image, (40, 40))
            surf.blit(img_scaled, (0, 0))
        else:
            # Stylized cube with border
            pygame.draw.rect(surf, self.color, (0, 0, 40, 40), border_radius=6)
            pygame.draw.rect(surf, (255, 255, 255, 60), (0, 0, 40, 40), 2, border_radius=6)

        # 3. Apply Rotation
        rotated_surf = pygame.transform.rotate(surf, self.angle)
        new_rect = rotated_surf.get_rect(center=self.rect.center)
        
        screen.blit(rotated_surf, new_rect.topleft)
