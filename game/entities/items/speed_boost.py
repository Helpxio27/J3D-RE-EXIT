# game/entities/items/speed_boost.py
from game.entities.items.base_item import BaseItem

DURATION = 4.0        # seconds
SPEED_MULT = 1.8

class SpeedBoost(BaseItem):
    def __init__(self):
        self.active = False      # ← make sure this is False not True
        self._timer = 0.0
        self._user_id = None
        self._original_speed = None

    def on_use(self, app, user_id: int):
        if self.active:          # ← already running, don't stack
            return
        sim = app.player_sims[user_id]
        self._user_id = user_id
        self._original_speed = sim.max_speed
        sim.max_speed = sim.max_speed * SPEED_MULT
        self._timer = DURATION
        self.active = True
        app.sounds.play("power_speed")

    def update(self, app):
        if not self.active:
            return
        self._timer -= app.render_dt
        if self._timer <= 0:
            # Reset speed
            if self._user_id is not None:
                sim = app.player_sims[self._user_id]
                sim.max_speed = self._original_speed
            self.active = False

    def draw(self, screen):
        pass  # no visual for speed boost | player just moves faster