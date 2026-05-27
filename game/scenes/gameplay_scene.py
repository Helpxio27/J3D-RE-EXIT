# game/scenes/gameplay_scene.py
import pygame
from game.entities.items.item_manager import ItemManager
from game.scenes.base_scene import BaseScene
from game.systems.timer_system import MatchTimerSystem
from game.world.camera import Camera
from config.settings import FIXED_DT, SCREEN_WIDTH, SCREEN_HEIGHT
from game.ui.hud import HUD
from game.systems.timer_system import MatchTimerSystem
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT
        
# Gameplay Scene Owns --> Camera
class GameplayScene(BaseScene):
    def __init__(self, app):
        self.app = app
        self.paused = False
        self._match_started = False
        self._start_timer = 0.0
        self._match_over = False
        self._handling_timeout = False

        # Always reset players on scene creation
        self.app._reset_players()

        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.item_manager = ItemManager()

        # HUD
        colors = [r.color for r in self.app.player_renders]
        self.hud = HUD(colors)

        # Timer — created once, set_tagger fires after countdown in update()
        duration = self.app.level.config.get("time_limit", 60.0)
        print(f"[TIMER] Starting with duration={duration}")
        self.timer_system = MatchTimerSystem(player_count=2, duration=duration)
        
    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.paused = not self.paused
            if self.paused and event.key == pygame.K_q:
                self.app.reset_to_menu()

            # Local only — online ability use goes through input packet
            if not self.app.online:
                for i, ctrl in enumerate(self.app.controls):
                    if event.key == ctrl.get("use_power"):
                        self._try_use_ability(i)
    
    def update(self, accumulator):
        if self.paused:
            return accumulator

        # Countdown before match starts
        if not self._match_started:
            self._start_timer = getattr(self, '_start_timer', 0) + self.app.render_dt
            if self._start_timer >= 3.0:    # 3 second delay
                self._match_started = True
                tagger_id = next((i for i, s in enumerate(self.app.player_sims) if s.is_tagger), 0)
                self.timer_system.set_tagger(tagger_id)
            return accumulator              # don't tick until started

        inputs = self.app._build_inputs()
        
        if self.app.online and hasattr(self.app, 'client') and self.app.client:
            local_id = self.app.client.player_id
            self.app.client.send_input(inputs[local_id])
            messages = self.app.client.receive()
            for msg in messages:
                if msg.get("type") == "state":
                    for p_data in msg["players"]:
                        pid = p_data.get("id")
                        if pid is None:
                            continue
                        sim = self.app.player_sims[pid]
                        if pid == local_id:
                            self.app.client.apply_correction(sim, p_data)
                        else:
                            sim.from_dict(p_data)

                    # Sync timers from server
                    if "timers" in msg:
                        for i, t_data in enumerate(msg["timers"]):
                            if i < len(self.timer_system.timers):
                                self.timer_system.timers[i].time_left = t_data["time_left"]
                                self.timer_system.timers[i].running   = t_data["running"]

                    # Sync abilities from server
                    if "abilities" in msg:
                        for pid_str, slot_data in msg["abilities"].items():
                            pid = int(pid_str)
                            if pid < len(self.hud.cards):
                                self.hud.cards[pid].ability_slot.ability_name = slot_data["name"]
                                self.hud.cards[pid].ability_slot.cooldown     = slot_data["cooldown"]

                elif msg.get("type") == "event":
                    self._handle_network_event(msg)

        while accumulator >= FIXED_DT:
            self._tick(inputs)
            accumulator -= FIXED_DT

        self.hud.update(self.app.render_dt, self.app.player_sims, self.timer_system)
        self.camera.update(self.app.render_dt)
        return accumulator

    
    def _tick(self, inputs):
        if self.app.online and hasattr(self.app, 'client') and self.app.client:
            local_id = self.app.client.player_id
            sim = self.app.player_sims[local_id]
            inp = inputs[local_id] if local_id < len(inputs) else {}
            sim.update(self.app.level.walls, inp)
        else:
            for i, sim in enumerate(self.app.player_sims):
                if sim.rect.top > SCREEN_HEIGHT + 200:
                    self._handle_timeout(i)
                    return
                inp = inputs[i] if i < len(inputs) else {}
                sim.update(self.app.level.walls, inp)

        for i, render in enumerate(self.app.player_renders):
            render.update(self.app.render_dt, self.app.player_sims[i])

        self.item_manager.update(self.app) 
        self._update_tag()
        self.timer_system.update(FIXED_DT)

        if self.timer_system.finished and not self._match_over:
            self._handle_timeout(self.timer_system.loser_id)

    def _update_tag(self):
        import random
        tagger = next((p for p in self.app.player_sims if p.is_tagger), None)
        runner = next((p for p in self.app.player_sims if not p.is_tagger), None)
        if tagger and runner and tagger.can_tag(runner):
            tagger.is_tagger = False
            runner.is_tagger = True
            tagger.tagback_cooldown = tagger.tagback_cooldown_time
            runner.vel_x = 0
            runner.vel_y = 0
            runner.stun_timer = 10

            # Randomize power for new tagger
            new_tagger_id = next(i for i, s in enumerate(self.app.player_sims) if s.is_tagger)
            powers = ["laser", "speed", "freeze", "glitch"]
            self.hud.cards[new_tagger_id].ability_slot.ability_name = random.choice(powers)
            self.hud.cards[new_tagger_id].ability_slot.cooldown = 0.0

            # Sync timer
            self.timer_system.set_tagger(new_tagger_id)

            self.camera.clear_queue()
            self.camera.add_action("shake", 14)
            self.app.sounds.play("tag")
    
    def _handle_timeout(self, loser_id: int):
        if self._match_over:
            return
        self._match_over = True

        winner_id = 1 - loser_id
        winner_color = self.app.player_renders[winner_id].color

        self.app.sounds.stop_music()
        self.app.sounds.play("tag")  # satisfying end sound

        from game.scenes.win_scene import WinScene
        self.app.replace_scene(WinScene(self.app, winner_id, winner_color))

    def _handle_network_event(self, msg: dict):
        event_type = msg.get("event")
        data       = msg.get("data", {})
        player_id  = msg.get("player_id")

        if event_type == "ability_used":
            ability   = data.get("ability")
            pid       = data.get("player_id", player_id)
            # Fire the ability locally for visual effect
            self.item_manager.use_ability(self.app, pid, ability)
            # Sync the HUD slot
            slot = self.hud.cards[pid].ability_slot
            slot.cooldown = 1.0
            slot.ability_name = None
        elif event_type == "void_death":
            loser_id = data.get("player_id")
            self._handle_timeout(loser_id)
        elif event_type == "timeout":
            loser_id = data.get("player_id")
            self._handle_timeout(loser_id)

    def _try_use_ability(self, player_id: int):
        slot = self.hud.cards[player_id].ability_slot
        if slot.ability_name and slot.cooldown <= 0:
            ability = slot.ability_name
            self.item_manager.use_ability(self.app, player_id, ability)
            slot.cooldown = 1.0
            slot.ability_name = None
            self.camera.shake(8)

            # Tell server about it
            if self.app.online and hasattr(self.app, 'client') and self.app.client:
                self.app.client.send_event("ability_used", {
                    "player_id": player_id,
                    "ability":   ability
                })
                
    def draw(self, screen):
        if self.paused:
            self._draw_pause(screen)
            return

        world_surface = pygame.Surface((screen.get_width(), screen.get_height()))
        world_surface.blit(self.app.background, (0, 0))
        self.app.renderer.draw(world_surface)
        self.app.level.draw(world_surface)
        for i, render in enumerate(self.app.player_renders):
            render.draw(world_surface, self.app.player_sims[i])
        self.item_manager.draw(world_surface)
        screen.blit(self.camera.apply(world_surface), (0, 0))

        # Countdown overlay
        if not self._match_started:
            countdown = max(1, 3 - int(getattr(self, '_start_timer', 0)))
            font = pygame.font.SysFont("Arial", 120, bold=True)
            text = font.render(str(countdown), True, (255, 220, 0))
            text.set_alpha(200)
            screen.blit(text, text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2)))

        self.hud.draw(screen, self.app.player_sims, self.timer_system,
                    screen.get_width(), screen.get_height())
    def _draw_pause(self, screen):
        # Defines a font and renders the pause text onto the screen
        font = pygame.font.SysFont(None, 48)
        # Font.render returns a new surface with the text drawn on it
        text = font.render("PAUSED  |  ESC = Resume  |  Q = Menu", True, (255, 255, 255))
        # Blit the text surface onto the main with pos 100, 100
        screen.blit(text, (100, 100))

