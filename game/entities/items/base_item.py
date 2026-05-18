import pygame
class BaseItem:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.active = True

    def on_pickup(self, player):
        pass  # each item overrides this

    def update(self):
        pass

    def draw(self, surface):
        pass