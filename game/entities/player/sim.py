# game/entities/player/sim.py
import pygame
from game.world.collision import resolve_horizontal, resolve_vertical, circle_rect_collision

class PlayerSim:
    def __init__(self, x, y, is_tagger=False):
        self.rect = pygame.Rect(x, y, 30, 30)

        # Physics
        self.vel_x = 0
        self.vel_y = 0
        self.accel_ground = 1.5
        self.accel_air = 0.4
        self.friction = 0.92
        self.max_speed = 10
        self.gravity = 0.8
        self.jump_strength = -15

        # State flags
        self.on_ground = False
        self.on_wall = False
        self.wall_dir = 0
        self.can_wall_jump = True

        # Wall jump
        self.wall_jump_x = 12
        self.wall_jump_y = -15

        # Tag mechanics
        self.is_tagger = is_tagger
        self.tag_radius = 30
        self.stun_timer = 0
        self.tagback_cooldown = 0
        self.tagback_cooldown_time = 30  # move to config/constants.py later

    # ========================
    # Input handling | DECIDES 
    # ========================
    def handle_input(self, inputs):
        wish_dir = 0
        if inputs.get("left"): wish_dir -= 1
        if inputs.get("right"): wish_dir += 1

        accel = self.accel_ground if self.on_ground else self.accel_air
        self.vel_x += wish_dir * accel

        if self.on_ground and wish_dir == 0:
            self.vel_x *= self.friction

        if wish_dir != 0 and ((wish_dir > 0 and self.vel_x < 0) or (wish_dir < 0 and self.vel_x > 0)):
            self.vel_x *= 0.7
            accel *= 1.5

        self.vel_x = max(-self.max_speed, min(self.vel_x, self.max_speed))

        if inputs.get("jump") and self.on_ground:
            self.vel_y = self.jump_strength
            self.on_ground = False

    # ===================================
    # Wall jump | DECIDES | CHECKS | DOES
    # ===================================
    def try_wall_jump(self, inputs):
        if inputs.get("jump") and self.on_wall and not self.on_ground and self.can_wall_jump:
            self.vel_x = -self.wall_dir * self.wall_jump_x
            self.vel_y = self.wall_jump_y
            self.can_wall_jump = False

    # ==============
    # Gravity | DOES
    # ==============
    def apply_gravity(self):
        if self.on_wall and not self.on_ground and self.vel_y > 4:
            self.vel_y = 4
        else:
            self.vel_y += self.gravity

    # =============
    # Update | DOES
    # =============
    def update(self, obstacles, inputs):
        if self.stun_timer > 0:
            self.stun_timer -= 1
            self.vel_x = 0
            self.vel_y = 0
            return

        if self.tagback_cooldown > 0:
            self.tagback_cooldown -= 1

        self.handle_input(inputs)
        self.try_wall_jump(inputs)
        self.apply_gravity()

        self.rect.x += self.vel_x
        self.vel_x, self.on_wall, self.wall_dir = resolve_horizontal(self.rect, obstacles, self.vel_x)

        self.rect.y += self.vel_y
        self.vel_y, self.on_ground = resolve_vertical(self.rect, obstacles, self.vel_y)

        if self.on_ground:
            self.can_wall_jump = True
            self.on_wall = False
            self.wall_dir = 0

    # ==============
    # Network | DOES
    # ==============
    def to_dict(self):
        return {
            "x": self.rect.x,
            "y": self.rect.y,
            "vx": self.vel_x,
            "vy": self.vel_y,
            "is_tagger": self.is_tagger
        }

    def from_dict(self, data):
        self.rect.x = data["x"]
        self.rect.y = data["y"]
        self.vel_x = data["vx"]
        self.vel_y = data["vy"]
        self.is_tagger = data["is_tagger"]

    # =============
    # Tag | DECIDES
    # =============
    def can_tag(self, other) -> bool:
        return (
            self.is_tagger
            and other.tagback_cooldown == 0
            and circle_rect_collision(self.rect.center, self.tag_radius, other.rect)
        )