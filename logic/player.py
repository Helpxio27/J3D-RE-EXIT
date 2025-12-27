import pygame
from particles import ParticleEmitter
from collision import resolve_collision_x, resolve_collision_y

class Player:
    def __init__(self, x, y): #INIT FUNCTION
        self.rect = pygame.Rect(x, y, 50, 50) # Player size 50x50

        # Physics
        self.vel_x = 0 
        self.vel_y = 0

        self.accel_ground = 1.5
        self.accel_air = 0.4

        self.friction = 0.92   # VERY IMPORTANT (close to 1)
        self.max_speed = 14    # FAST AS HELL
       
        self.gravity = 0.8 # Gravity affecting the player
        self.jump_strength = -15 # Jumping velocity (negative for upward movement)
        self.max_fall_speed = 20
        
        self.on_ground = False # To check if the player is on the ground
    
        # Particle Emitter for effects
        self.trail = ParticleEmitter()

        #WAll 
        self.on_wall = False    #le joueur touche un mur
        self.wall_dir = 0       #mur gauche = -1 et mur droit = 1 
        self.wall_slide_speed = 4   #vitesse de la chute
        #wall jump
        self.wall_jump = pygame.Vector2(12,-15)
        self.can_wall_jump = True
        #jump buffer
        self.jump_buffer = 0
        self.jump_buffer_time = 8 #frames

        self.trail = ParticleEmitter()
    
    
    # ================================== # 
    # HELPER FUNCTION
    def get_wish_dir(self, keys):
        # Directional Input :
        # wish_dir = -1   left
        # wish_dir = 1    right
        # wish_dir = 0    no input
        dir = 0
        if keys[pygame.K_a]:
            dir -= 1
        if keys[pygame.K_d]:
            dir += 1
        return dir
    # ================================== # 
    # HANDLING INPUT
    def handle_input(self): 
        keys = pygame.key.get_pressed()

        wish_dir = self.get_wish_dir(keys)
        self.apply_horizontal_movement(wish_dir)
        self.handle_jump(keys)
        self.handle_drop(keys)

    def handle_jump(self, keys):
        if keys[pygame.K_SPACE]:
            self.jump_buffer = self.jump_buffer_time

        if self.jump_buffer > 0:
            self.jump_buffer -= 1

        if self.jump_buffer > 0 and self.on_ground:      # Jump normal si sol
            self.vel_y = self.jump_strength
            self.on_ground = False
            self.jump_buffer = 0
            self.can_wall_jump = True

    def handle_drop(self, keys):
        if keys[pygame.K_s] and not self.on_ground:
            self.vel_y += self.gravity * 6
    # ================================== #
    # APPLICATION OF MOVEMENT
    def apply_horizontal_movement(self, wish_dir):
        # Choose acceleration
        accel = self.accel_ground if self.on_ground else self.accel_air

        # Apply movement
        self.vel_x += wish_dir * accel

        # Apply friction only on ground and no input
        if self.on_ground and wish_dir == 0:
            self.vel_x *= self.friction

        # Sharp turn handling
        if wish_dir != 0 and ((wish_dir > 0 and self.vel_x < 0) or (wish_dir < 0 and self.vel_x > 0)):
            # Sharp turn penalty
            self.vel_x *= 0.7
            accel *= 1.5
        
        # Clamp velocity
        self.vel_x = max(-self.max_speed, min(self.vel_x, self.max_speed))  
    
    def apply_gravity(self):
        if self.on_wall and not self.on_ground and self.vel_y > self.wall_slide_speed:   #wall slide
            self.vel_y = self.wall_slide_speed
        else:
            self.vel_y += self.gravity
        self.vel_y = min(self.vel_y, self.max_fall_speed)

    def try_wall_jump(self):
        if self.on_wall and self.jump_buffer > 0 and self.can_wall_jump:
            self.vel_x = -self.wall_dir * self.wall_jump.x
            self.vel_y = self.wall_jump.y
            self.can_wall_jump = False
            self.jump_buffer = 0
    # ================================== #
    # UPDATE AND DRAW (low level)
    def update(self, colliders):
        self.on_ground = False         # pour reset
        self.on_wall = False
        self.wall_dir = 0
        
        self.handle_input()
        self.apply_gravity()
        self.try_wall_jump()

        self.rect.x += self.vel_x
        for c in colliders:                       # collisions hori
            self.vel_x, self.on_wall, self.wall_dir = resolve_collision_x(self.rect, c, self.vel_x)
        self.rect.y += self.vel_y

        self.rect.y += self.vel_y
        for c in colliders:                       # collision verti
            self.vel_y, self.on_ground = resolve_collision_y(self.rect, c, self.vel_y)


        speed = abs(self.vel_x) + abs(self.vel_y)
        if speed > 5:
            self.trail.emit(
                pos=(self.rect.centerx, self.rect.centery),
                # vel=(10 * self.vel_x , 10 * self.vel_x),
                vel=(10, 10),
                amount=2,
                spread=1,
                color=(200, 200, 200),
                size=3,
                lifetime=1
            )
        self.trail.update(1 / 60)

    def draw(self, screen):
        # Trail emitter draw
        self.trail.draw(screen)

        # Basic Drawing of player
        pygame.draw.rect(screen, (200, 50, 50), self.rect)