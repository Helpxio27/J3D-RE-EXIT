# game/entities/items/base_item.py
import pygame

class BaseItem:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.active = True

    def on_use(self, app, user_id: int):
        """DECIDES + DOES: triggered when player uses this ability"""
        pass

    def update(self, app):
        """DOES: advances item state one tick"""
        pass

    def draw(self, screen):
        """DOES: renders the item"""
        pass