import pygame
import json

# This is probably the hardest code I've ever fucking done man
# Shoot me already
# Do not ask me to redo it, I will not be able

class Level:
    def __init__(self, map_path, tileset_path):
        # Load map JSON
        with open(map_path) as f: # Makes a dictionary
            self.map_data = json.load(f)

        self.map_width = self.map_data["width"]
        self.map_height = self.map_data["height"]
        self.tile_size = self.map_data["tilewidth"]  # assuming square tiles

        # --- Load tileset ---
        self.tiles = self.load_tileset(tileset_path, self.tile_size, self.tile_size)

        # --- Build collision walls ---
        # first layer is the collision layer
        collision_layer = self.map_data['layers'][0]
        tile_ids = collision_layer['data']

        self.walls = []
        for index, tile_id in enumerate(tile_ids):
            if tile_id != 0:  # 0 = empty tile
                x = (index % self.map_width) * self.tile_size
                y = (index // self.map_width) * self.tile_size
                self.walls.append(pygame.Rect(x, y, self.tile_size, self.tile_size))

    def load_tileset(self, tileset_path, tile_width, tile_height):
        """Load a single tileset image and split it into tile surfaces."""
        tileset_image = pygame.image.load(tileset_path).convert_alpha()
        tiles = {}

        tileset_width, tileset_height = tileset_image.get_size()
        tile_id = 1  # Tiled tile IDs usually start at 1

        for y in range(0, tileset_height, tile_height):
            for x in range(0, tileset_width, tile_width):
                rect = pygame.Rect(x, y, tile_width, tile_height)
                image = tileset_image.subsurface(rect)
                tiles[tile_id] = image
                tile_id += 1

        return tiles
    
    def draw(self, screen, scale_x=1, scale_y=1):
        layer = self.map_data['layers'][0]
        tile_ids = layer['data']

        for index, tile_id in enumerate(tile_ids):
            if tile_id == 0:
                continue

            x = (index % self.map_width) * self.tile_size * scale_x
            y = (index // self.map_width) * self.tile_size * scale_y

            image = self.tiles.get(tile_id)
            if image:
                scaled_image = pygame.transform.scale(
                    image,
                    (int(self.tile_size * scale_x), int(self.tile_size * scale_y))
                )
                screen.blit(scaled_image, (x, y))

# All decoration system
class MapRenderer:
    def __init__(self, level):
        self.level = level

    def draw(self, screen):
        # start at layer 1 because layer 0 is collisions
        for layer_index in range(1, len(self.level.map_data["layers"])):

            layer = self.level.map_data["layers"][layer_index]
            tile_ids = layer["data"]

            for index, tile_id in enumerate(tile_ids):
                if tile_id == 0:
                    continue

                x = (index % self.level.map_width) * self.level.tile_size 
                y = (index // self.level.map_width) * self.level.tile_size 

                image = self.level.tiles.get(tile_id)

                if image:
                    screen.blit(image, (x, y))

# OLD IMPLEMENTATION:
# for debugging collisions
#import pygame
#from settings import SCREEN_WIDTH, SCREEN_HEIGHT

# TILE_SIZE = 16

# LEVEL_DATA = [
#     "#######################################################",
#     "#.....................................................#",
#     "#.....................................................#",
#     "#.....................................................#",
#     "#.....................................................#",
#     "#.....................................................#",
#     "#.....................................................#",
#     "#.....................................................#",
#     "#.....................................................#",
#     "#.....................................................#",
#     "#.............................##########..............#",
#     "#.....................................................#",
#     "#.....................................................#",
#     "#.....................................................#",
#     "#.........#########...................................#",
#     "#.....................................................#",
#     "#.....................................................#",
#     "#.....................................................#",
#     "#................................#....................#",
#     "#................................#....................#",
#     "#................................#....................#",
#     "#................................#....................#",
#     "#................................#.....................",
#     "#........................#########.....................",
#     "#......................................................",
#     "#..........########....................#######.........",
#     "#......................................................",
#     "#......................................................",
#     "#......................................................",
#     "#######################################################",
# ]

# class Level:
#     def __init__(self):
#         self.walls = []
#         self.load_level()

#     def load_level(self):
#         for y, row in enumerate(LEVEL_DATA):
#             for x, tile in enumerate(row):
#                 if tile == "#":
#                     self.walls.append(
#                         pygame.Rect(
#                             x * TILE_SIZE,
#                             y * TILE_SIZE,
#                             TILE_SIZE,
#                             TILE_SIZE
#                         )
#                     )

#     def draw(self, screen):
#         for wall in self.walls:
#             pygame.draw.rect(screen, (200, 200, 200), wall)

    