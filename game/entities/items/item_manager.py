# game/entities/items/item_manager.py
from game.entities.items.speed_boost import SpeedBoost
from game.entities.items.laser import Laser
from game.entities.items.homing_cube import HomingCube

ABILITY_MAP = {
    "speed":  SpeedBoost,
    "laser":  Laser,
    "freeze": lambda: HomingCube("freeze"),
    "glitch": lambda: HomingCube("glitch"),
}

class ItemManager:
    def __init__(self):
        # One active ability instance per player
        self._active = {}   # { player_id: item_instance }

    def use_ability(self, app, player_id: int, ability_name: str):
        """DOES: instantiates and fires the ability"""
        if ability_name not in ABILITY_MAP:
            return
        item = ABILITY_MAP[ability_name]()
        item.on_use(app, player_id)
        self._active[player_id] = item

    def update(self, app):
        for item in list(self._active.values()):
            item.update(app)
        # Clean up finished items
        self._active = {
            pid: item for pid, item in self._active.items()
            if item.active
        }

    def draw(self, screen):
        for item in self._active.values():
            item.draw(screen)