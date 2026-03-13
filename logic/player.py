import pygame
import math
import random
from particles import ParticleEmitter
from collision import resolve_horizontal
from collision import resolve_vertical
from settings import SCREEN_HEIGHT 
from settings import SCREEN_WIDTH

class Player:
    def __init__(self, x, y, controls, color, is_tagger=False):
        self.rect = pygame.Rect(x, y, 30, 30) 

        self.controls = controls
        self.color = color
        self.is_tagger = is_tagger
        
        # Customization
        self.custom_image = None
        self.angle = 0 

        # Physics 
        self.vel_x = 0 
        self.vel_y = 0
        self.accel_ground = 1.5
        self.accel_air = 0.4
        self.friction = 0.92
        self.max_speed = 10 
        self.gravity = 0.8 
        self.jump_strength = -15 
        self.on_ground = False 
        
        # Tag Mechanics
        self.tag_radius = 30
        self.tagback_cooldown = 0
        self.tagback_cooldown_time = 30

        # Wall Mechanics
        self.on_wall = False
        self.wall_dir = 0 
        self.wall_slide_speed = 4
        self.wall_jump_x = 12 
        self.wall_jump_y = -15 
        self.can_wall_jump = True
        
        # Internal Trail
        self.trail = ParticleEmitter()

    def get_wish_dir(self, keys):
        direction = 0
        if keys[self.controls["left"]]: direction -= 1
        if keys[self.controls["right"]]: direction += 1
        return direction

    def handle_input(self, emitter): 
        keys = pygame.key.get_pressed()
        wish_dir = self.get_wish_dir(keys)
        self.apply_horizontal_movement(wish_dir)
        self.handle_jump(keys, emitter)
        self.handle_drop(keys)

    def handle_jump(self, keys, emitter):
        if keys[self.controls["jump"]] and self.on_ground:
            self.vel_y = self.jump_strength
            self.on_ground = False
            
            # --- IMPROVED SMOKE EFFECT ---
            if emitter:
                for _ in range(15):  # More particles for a dense effect
                    speed_x = random.uniform(-4, 4) # Lateral explosion
                    speed_y = random.uniform(-1, 1) # Slight vertical movement
                    
                    emitter.emit(
                        pos=(self.rect.centerx, self.rect.bottom),
                        vel=(speed_x, speed_y),
                        amount=1, 
                        spread=2, 
                        color=(220, 220, 220), # Smoke color
                        size=random.randint(3, 7), # Varied sizes
                        lifetime=random.uniform(0.4, 0.8),
                        alpha=random.randint(150, 200),
                        fade_curve='ease-out'
                    )

    def handle_drop(self, keys):
        if keys[self.controls["drop"]] and not self.on_ground:
            self.vel_y += self.gravity * 6

    def apply_horizontal_movement(self, wish_dir):
        accel = self.accel_ground if self.on_ground else self.accel_air
        self.vel_x += wish_dir * accel
        
        if self.on_ground and wish_dir == 0:
            self.vel_x *= self.friction
            
        # Sharp turn penalty
        if wish_dir != 0 and ((wish_dir > 0 and self.vel_x < 0) or (wish_dir < 0 and self.vel_x > 0)):
            self.vel_x *= 0.7 
            
        self.vel_x = max(-self.max_speed, min(self.vel_x, self.max_speed))  
    
    def apply_gravity(self):
        # Wall slide logic
        if self.on_wall and not self.on_ground and self.vel_y > self.wall_slide_speed:
            self.vel_y = self.wall_slide_speed
        else:
            self.vel_y += self.gravity

    def try_wall_jump(self, keys):
        if keys[self.controls["jump"]] and self.on_wall and not self.on_ground and self.can_wall_jump:
            self.vel_x = -self.wall_dir * self.wall_jump_x
            self.vel_y = self.wall_jump_y
            self.can_wall_jump = False

    def update_animation(self):
        """Dynamic Tilt Effect"""
        target_angle = -self.vel_x * 2.5 
        self.angle += (target_angle - self.angle) * 0.15

    def update(self, obstacles, render_dt, emitter=None):
        keys = pygame.key.get_pressed()
        self.handle_input(emitter)
        self.apply_gravity()
        self.try_wall_jump(keys)

        # Movement and Collisions
        self.rect.x += self.vel_x
        self.vel_x, self.on_wall, self.wall_dir = resolve_horizontal(self.rect, obstacles, self.vel_x)

        self.rect.y += self.vel_y
        self.vel_y, self.on_ground = resolve_vertical(self.rect, obstacles, self.vel_y)
        
        if self.on_ground:
            self.can_wall_jump = True
            self.on_wall = False
            self.wall_dir = 0

        self.update_animation()

        # --- IMPROVED COLORED TRAIL ---
        speed = abs(self.vel_x) + abs(self.vel_y)
        if speed > 6:
            self.trail.emit(
                pos=(self.rect.centerx, self.rect.centery),
                vel=(random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)), 
                amount=1, 
                spread=1, 
                color=self.color, 
                size=random.randint(2, 4), 
                lifetime=0.25, 
                alpha=130, 
                fade_curve='ease-in'
            )
        self.trail.update(render_dt)
        
        if self.tagback_cooldown > 0:
            self.tagback_cooldown -= 1

        # Respawn if falling out of bounds
        if self.rect.y >= SCREEN_HEIGHT + 500:
            self.rect.x, self.rect.y = 300, 100
            self.vel_x, self.vel_y = 0, 0

    def draw(self, screen):
        # 1. Tagger Halo (Smooth pulse)
        if self.is_tagger:
            # Animated outer circle
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.01)) * 5
            pygame.draw.circle(screen, (255, 255, 0), self.rect.center, self.tag_radius + pulse, 2)

        # 2. Behind particles
        self.trail.draw(screen)

        # 3. Draw Player with Rotation (Tilt)
        player_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        if self.custom_image:
            img_scaled = pygame.transform.scale(self.custom_image, (self.rect.width, self.rect.height))
            player_surf.blit(img_scaled, (0, 0))
        else:
            # Modern Cube look with light border
            pygame.draw.rect(player_surf, self.color, (0, 0, self.rect.width, self.rect.height), border_radius=5)
            pygame.draw.rect(player_surf, (255, 255, 255, 50), (0, 0, self.rect.width, self.rect.height), 2, border_radius=5)

        rotated_surf = pygame.transform.rotate(player_surf, self.angle)
        new_rect = rotated_surf.get_rect(center=self.rect.center)
        
        screen.blit(rotated_surf, new_rect.topleft)
