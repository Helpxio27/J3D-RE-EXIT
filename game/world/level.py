# game/world/level.py
import pygame
import json
import os
from tools.path import resource_path

class Level:
    def __init__(self, map_folder):
        # Everything is derived from the folder now
        folder = resource_path(map_folder)
        cfg_path = os.path.join(folder, "config.json")

        with open(cfg_path) as f:
            self.config = json.load(f)

        map_path     = os.path.join(folder, self.config["map"])
        tileset_path = os.path.join(folder, self.config["tileset"])

        # Load map
        with open(map_path) as f:
            self.map_data = json.load(f)

        self.map_width  = self.map_data["width"]
        self.map_height = self.map_data["height"]
        self.tile_size  = self.map_data["tilewidth"]
        self.tiles      = self._load_tileset(tileset_path, self.tile_size)

        # Collision walls from layer 0
        self.walls = []
        for index, tile_id in enumerate(self.map_data["layers"][0]["data"]):
            if tile_id != 0:
                x = (index % self.map_width) * self.tile_size
                y = (index // self.map_width) * self.tile_size
                self.walls.append(pygame.Rect(x, y, self.tile_size, self.tile_size))

        # Spawn points from config (fallback to defaults)
        self.spawn_points = self.config.get("spawn_points", [[500, 700], [300, 700]])

    def _load_tileset(self, tileset_path, tile_size):
        image = pygame.image.load(tileset_path).convert_alpha()
        tiles = {}
        tile_id = 1
        for y in range(0, image.get_height(), tile_size):
            for x in range(0, image.get_width(), tile_size):
                tiles[tile_id] = image.subsurface(pygame.Rect(x, y, tile_size, tile_size))
                tile_id += 1
        return tiles

    def draw(self, screen, scale_x=1, scale_y=1):
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