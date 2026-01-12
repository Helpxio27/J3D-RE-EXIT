import pygame

class Player:
    def __init__(self, x, y, controls, color):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.controls = controls
        self.color = color
        self.speed = 5

    def update(self):
        keys = pygame.key.get_pressed()

        if keys[self.controls["left"]]:
            self.rect.x -= self.speed
        if keys[self.controls["right"]]:
            self.rect.x += self.speed
        if keys[self.controls["up"]]:
            self.rect.y -= self.speed
        if keys[self.controls["down"]]:
            self.rect.y += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
