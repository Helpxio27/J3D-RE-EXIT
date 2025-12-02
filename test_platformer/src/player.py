import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((32, 48))
        self.image.fill((80, 180, 255))
        self.rect = self.image.get_rect(topleft=pos)

        self.vel = pygame.math.Vector2(0, 0)
        self.speed = 4
        self.gravity = 0.5
        self.jump_power = -10
        self.on_ground = False

    def apply_gravity(self):
        self.vel.y += self.gravity
        self.rect.y += self.vel.y

    def update(self, tiles):
        keys = pygame.key.get_pressed()

        # Horizontal movement
        self.vel.x = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * self.speed
        self.rect.x += self.vel.x

        # Horizontal collisions
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.vel.x > 0:  # moving right
                    self.rect.right = tile.rect.left
                elif self.vel.x < 0:  # moving left
                    self.rect.left = tile.rect.right

        # Jump
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel.y = self.jump_power
            self.on_ground = False

        # Apply gravity
        self.apply_gravity()

        # Vertical collisions
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.vel.y > 0:
                    self.rect.bottom = tile.rect.top
                    self.vel.y = 0
                    self.on_ground = True
                elif self.vel.y < 0:
                    self.rect.top = tile.rect.bottom
                    self.vel.y = 0

