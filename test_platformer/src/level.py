import pygame
from settings import TILE_SIZE
from .player import Player
from .tile import Tile

class Level:
    def __init__(self, map_file):
        self.tiles = pygame.sprite.Group()
        self.player = pygame.sprite.GroupSingle(Player((100, 300)))
        self.load_level(map_file)

    def load_level(self, map_file):
        with open(map_file) as f:
            rows = f.read().splitlines()

        for y, row in enumerate(rows):
            for x, char in enumerate(row):
                if char == "X":
                    self.tiles.add(Tile((x * TILE_SIZE, y * TILE_SIZE)))

    def update(self):
        self.player.sprite.update(self.tiles)

    def draw(self, screen):
        self.tiles.draw(screen)
        self.player.draw(screen)

