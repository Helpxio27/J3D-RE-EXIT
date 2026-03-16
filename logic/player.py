import pygame
from particles import ParticleEmitter
from collision import resolve_horizontal
from collision import resolve_vertical
from settings import SCREEN_HEIGHT 
from settings import SCREEN_WIDTH


class Player:
    def __init__(self, x, y, controls, color, is_tagger=False): #INIT FUNCTION
        self.rect = pygame.Rect(x, y, 30, 30) # Player size

        self.controls = controls
        self.color = color
        self.is_tagger = is_tagger
        
        # Tag mechanics
        self.tag_radius = 60

        self.tagback_cooldown = 0      # frames until this player can be tagged by the last runner
        self.tagback_cooldown_time = 30  # e.g., 0.5s at 60 FPS

        # Physics
        self.vel_x = 0 
        self.vel_y = 0

        self.accel_ground = 1.5
        self.accel_air = 0.4

        self.friction = 0.92   # VERY IMPORTANT (close to 1)
        self.max_speed = 10    # FAST AS HELL

        self.gravity = 0.8 # Gravity affecting the player
        self.jump_strength = -15 # Jumping velocity (negative for upward movement)

        self.on_ground = False # To check if the player is on the ground
        
        # Tagging Logic
        self.is_tagger = is_tagger
        self.tag_radius = 30
        self.stun_timer = 0
        
        # Animations
        self.angle = 0
        self.target_angle = 15

        # Wall slide mechanics
        self.on_wall = False
        self.wall_dir = 0   # -1 = left wall, 1 = right wall
        self.wall_slide_speed = 4

        # Wall jump mechanics
        self.wall_jump_x = 12     # horizontal push
        self.wall_jump_y = -15   # vertical force
        self.can_wall_jump = True
        
        # Particle Emitter for effects
        self.trail = ParticleEmitter()

    # ================================== # 
    # HELPER FUNCTION``
        # Directional Input :
        # wish_dir = -1   left
        # wish_dir = 1    right
        # wish_dir = 0    no input
    def get_wish_dir(self, inputs):
        dir = 0
        if inputs["left"]:
            dir -= 1
        if inputs["right"]:
            dir += 1
        return dir
    # ================================== # 
    # HANDLING INPUT
    def handle_input(self, inputs): 
        wish_dir = self.get_wish_dir(inputs)
        self.apply_horizontal_movement(wish_dir)
        self.handle_jump(inputs)
        self.handle_drop(inputs)

    def handle_jump(self, inputs):
        if inputs["jump"] and self.on_ground:
            self.vel_y = self.jump_strength
            self.on_ground = False

    def handle_drop(self, inputs):
        if inputs["drop"] and not self.on_ground:
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
        if self.on_wall and not self.on_ground and self.vel_y > self.wall_slide_speed:
            # Celeste-style wall slide (clamp fall speed)
            self.vel_y = self.wall_slide_speed
        else:
            self.vel_y += self.gravity

    def update_animation(self):
        # tilt based on horizontal velocity
        target_angle = max(-20, min(20, -self.vel_x * 2.5)) # keeps between -20 and 20
        # smooth interpolation
        self.angle += (target_angle - self.angle) * 0.15

    def try_wall_jump(self, inputs):
        if (
            inputs["jump"]
            and self.on_wall
            and not self.on_ground
            and self.can_wall_jump
        ):
            self.vel_x = -self.wall_dir * self.wall_jump_x
            self.vel_y = self.wall_jump_y
            self.can_wall_jump = False
    # def apply_gravity(self):
    #     self.vel_y += self.gravity

    #     max_fall_speed = 20
    #     self.vel_y = min(self.vel_y, max_fall_speed)
    # # ================================== #
    # UPDATE AND DRAW (low level)
    def update(self, obstacles, render_dt, inputs):
        self.handle_input(inputs)
        self.apply_gravity()
        self.try_wall_jump(inputs)
        self.update_animation()
        
        # Horizontal movement
        self.rect.x += self.vel_x
        self.vel_x, self.on_wall, self.wall_dir = resolve_horizontal(
            self.rect, obstacles, self.vel_x
        )

        # Vertical movement
        self.rect.y += self.vel_y
        self.vel_y, self.on_ground = resolve_vertical(
            self.rect, obstacles, self.vel_y
        )
        
        # RESET WALL JUMP WHEN LANDED
        if self.on_ground:
            self.can_wall_jump = True

        # If we're on the ground, we're not on a wall
        if self.on_ground:
            self.on_wall = False
            self.wall_dir = 0

        # Trail emitter update
        # NEED REWORK for better particle effect
        speed = abs(self.vel_x) + abs(self.vel_y)
        if speed > 5:
            self.trail.emit(
                pos=(self.rect.centerx, self.rect.centery),
                vel=(0, 0),
                amount=3,
                spread=1.5,
                color=(255, 255, 255),
                size=4,
                lifetime=0.1,
                alpha=150,
                fade_curve='ease-out'
            )
        self.trail.update(render_dt)
        
        # Tag Cooldown decreaser
        if self.tagback_cooldown > 0:
            self.tagback_cooldown -= 1
        
        if self.stun_timer > 0:
            self.stun_timer -= 1
            self.vel_x = 0
            self.vel_y = 0
            return
        
        # Respawn if go in da void :D
        if self.rect.x >= SCREEN_HEIGHT + 300 or self.rect.y >= SCREEN_HEIGHT + 300:
            self.rect.x = 300
            self.rect.y = 300

        # Test Tag Cooldown
        #print("Tag Cooldown", self.tagback_cooldown)

    def draw(self, screen):
        # If tagger
        if self.is_tagger:
            pygame.draw.circle(
                screen,
                (255, 255, 0),
                self.rect.center,
                self.tag_radius,
                5  # outline only
            )

        # Trail emitter draw
        #self.trail.draw(screen, blend_mode=pygame.BLEND_ADD)  # glowy effect
        self.trail.draw(screen)

        # Basic Drawing of player
        outline = 2
        player_surf = pygame.Surface(
            (self.rect.width + outline*2, self.rect.height + outline*2),
            pygame.SRCALPHA
        )

        # White outline
        pygame.draw.rect(
            player_surf,
            (255, 255, 255),
            (0, 0, self.rect.width + outline*2, self.rect.height + outline*2),
            border_radius=6
        )

        # Player body
        pygame.draw.rect(
            player_surf,
            self.color,
            (outline, outline, self.rect.width, self.rect.height),
            border_radius=4
        )

        rotated_surf = pygame.transform.rotate(player_surf, self.angle)
        new_rect = rotated_surf.get_rect(center=self.rect.center)

        screen.blit(rotated_surf, new_rect.topleft)

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
