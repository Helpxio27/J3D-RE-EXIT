# game/scenes/base_scene.py
class BaseScene:
    """Every scene must implement these three methods"""

    def handle_events(self, event):
        pass

    def update(self, dt):
        pass

    def draw(self, screen):
        pass