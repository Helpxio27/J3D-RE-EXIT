# game/systems/timer_system.py

class PlayerTimer:
    def __init__(self, duration: float):
        self.duration = duration
        self.time_left = duration
        self.running = False

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

    def reset(self):
        self.time_left = self.duration

    @property
    def expired(self) -> bool:
        return self.time_left <= 0

    def update(self, dt: float):
        if self.running and self.time_left > 0:
            self.time_left -= dt
            if self.time_left < 0:
                self.time_left = 0

    def format(self) -> str:
        """Returns MM:SS string"""
        total = max(0, int(self.time_left))
        mins = total // 60
        secs = total % 60
        return f"{mins:02d}:{secs:02d}"


class MatchTimerSystem:
    def __init__(self, player_count: int, duration: float = 60.0):
        self.timers = [PlayerTimer(duration) for _ in range(player_count)]
        self.finished = False
        self.loser_id = None

    def set_tagger(self, tagger_id: int):
        """DOES: starts tagger timer, stops all others"""
        for i, timer in enumerate(self.timers):
            if i == tagger_id:
                timer.start()
            else:
                timer.stop()

    def update(self, dt: float):
        if self.finished:
            return
        for i, timer in enumerate(self.timers):
            timer.update(dt)
            if timer.expired and not self.finished:
                self.finished = True
                self.loser_id = i

    def get_tagger_id(self, player_sims) -> int | None:
        for i, sim in enumerate(player_sims):
            if sim.is_tagger:
                return i
        return None