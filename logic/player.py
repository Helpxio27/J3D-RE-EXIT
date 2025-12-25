import pygame
from particles import ParticleEmitter
from collision import check_rect_collision # pretty damn useless function
from collision import resolve_platform_collision # AABB collision resolution for platforms

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

        self.on_ground = False # To check if the player is on the ground
    
        # Particle Emitter for effects
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
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = self.jump_strength
            self.on_ground = False

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
        self.vel_y += self.gravity

        max_fall_speed = 20
        self.vel_y = min(self.vel_y, max_fall_speed)
    # ================================== #
    # UPDATE AND DRAW (low level)
    def update(self):
        self.handle_input()
        self.apply_gravity()

        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        # Collision with platforms (NOT YET FINISHED !!!)
        # Need platform.py and collision.py for this to work
        #for plat in platform_list:
        #    self.vel_x, self.vel_y, self.on_ground = resolve_platform_collision(
        #        self.rect, plat.rect, self.vel_x, self.vel_y
        #    )

        # Trail emitter update
        # NEED REWORK for better particle effect
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






# Old Input Handling 

# def handle_input(self):
    #     keys = pygame.key.get_pressed()


    #     # Directional Input :
    #     # wish_dir = -1   left
    #     # wish_dir = 1    right
    #     # wish_dir = 0    no input
        
    #     wish_dir = 0
    #     if keys[pygame.K_a]:
    #         wish_dir -= 1
    #     if keys[pygame.K_d]:
    #         wish_dir += 1
        
    #     accel = self.accel_ground if self.on_ground else self.accel_air
       
    #     self.vel_x = max(-self.max_speed, min(self.vel_x, self.max_speed))
        
    #     self.vel_x += wish_dir * accel

    #     # Apply friction ONLY on ground and only if no input
    #     if self.on_ground and wish_dir == 0:
    #         self.vel_x *= self.friction
        
    #     self.vel_x = max(-self.max_speed, min(self.vel_x, self.max_speed))

    #     if keys[pygame.K_SPACE] and self.on_ground:
    #         self.vel_y = self.jump_strength
    #         self.on_ground = False
