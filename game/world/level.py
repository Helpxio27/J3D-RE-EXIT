# game/world/level.py
import pygame
import json
from tools.path import resource_path

class Level:
    def __init__(self, map_path, tileset_path):
        map_path = resource_path(map_path)
        tileset_path = resource_path(tileset_path)

        with open(map_path) as f:
            self.map_data = json.load(f)

        self.map_width  = self.map_data["width"]
        self.map_height = self.map_data["height"]
        self.tile_size  = self.map_data["tilewidth"]

        self.tiles = self._load_tileset(tileset_path, self.tile_size)

        # Layer 0 = collision layer
        collision_layer = self.map_data["layers"][0]
        self.walls = []
        for index, tile_id in enumerate(collision_layer["data"]):
            if tile_id != 0:
                x = (index % self.map_width) * self.tile_size
                y = (index // self.map_width) * self.tile_size
                self.walls.append(pygame.Rect(x, y, self.tile_size, self.tile_size))

    def _load_tileset(self, tileset_path, tile_size):
        """Slices the tileset image into a dict of {tile_id: Surface}"""
        image = pygame.image.load(tileset_path).convert_alpha()
        tiles = {}
        tile_id = 1  # Tiled IDs start at 1
        for y in range(0, image.get_height(), tile_size):
            for x in range(0, image.get_width(), tile_size):
                tiles[tile_id] = image.subsurface(pygame.Rect(x, y, tile_size, tile_size))
                tile_id += 1
        return tiles

    def draw(self, screen, scale_x=1, scale_y=1):
        """Draws layer 0 (collision tiles)"""
        for index, tile_id in enumerate(self.map_data["layers"][0]["data"]):
            if tile_id == 0:
                continue
            x = (index % self.map_width) * self.tile_size * scale_x
            y = (index // self.map_width) * self.tile_size * scale_y
            image = self.tiles.get(tile_id)
            if image:
                screen.blit(
                    pygame.transform.scale(image, (int(self.tile_size * scale_x), int(self.tile_size * scale_y))),
                    (x, y)
                )


class MapRenderer:
    """Draws all decoration layers (everything above layer 0)"""
    def __init__(self, level):
        self.level = level

    def draw(self, screen):
        for layer in self.level.map_data["layers"][1:]:
            for index, tile_id in enumerate(layer["data"]):
                if tile_id == 0:
                    continue
                x = (index % self.level.map_width) * self.level.tile_size
                y = (index // self.level.map_width) * self.level.tile_size
                image = self.level.tiles.get(tile_id)
                if image:
                    screen.blit(image, (x, y))