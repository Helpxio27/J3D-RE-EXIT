# game/scenes/gameplay_scene.py
import pygame
from game.scenes.base_scene import BaseScene
from game.world.camera import Camera
from config.settings import FIXED_DT, SCREEN_WIDTH, SCREEN_HEIGHT


# Gameplay Scene Owns --> Camera


class GameplayScene(BaseScene):
    def __init__(self, app):
        self.app = app
        self.paused = False
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

    def handle_events(self, event): # Pausing and input handling
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.paused = not self.paused
            if self.paused and event.key == pygame.K_q:
                self.app.reset_to_menu()
    
    def update(self, accumulator):
        if self.paused:
            return accumulator
        inputs = self.app._build_inputs()
        # Send local input to server
        if self.app.online and hasattr(self.app, 'client') and self.app.client:
            print(f"[CLIENT] id={self.app.client.player_id} room={self.app.client.room_code} tick={self.app.client.tick}") # Debug
            local_id = self.app.client.player_id
            self.app.client.send_input(inputs[local_id])
            # Apply server corrections for all players
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
                            sim.from_dict(p_data)  # remote — always snap to truth

        # Tick
        while accumulator >= FIXED_DT:
            self._tick(inputs)
            accumulator -= FIXED_DT

        self.camera.update(self.app.render_dt)
        return accumulator
    
    def _tick(self, inputs):
        if self.app.online and hasattr(self.app, 'client') and self.app.client:
            local_id = self.app.client.player_id
            # Only simulate local player — remote player comes from server
            sim = self.app.player_sims[local_id]
            inp = inputs[local_id] if local_id < len(inputs) else {}
            sim.update(self.app.level.walls, inp)
        else:
            # Offline — simulate all players locally
            for i, sim in enumerate(self.app.player_sims):
                inp = inputs[i] if i < len(inputs) else {}
                sim.update(self.app.level.walls, inp)

        # Always update renders for all players
        for i, render in enumerate(self.app.player_renders):
            render.update(self.app.render_dt, self.app.player_sims[i])

        self._update_tag()

    def _update_tag(self):
        tagger = next((p for p in self.app.player_sims if p.is_tagger), None)
        runner = next((p for p in self.app.player_sims if not p.is_tagger), None)
        if tagger and runner and tagger.can_tag(runner):
            tagger.is_tagger = False
            runner.is_tagger = True
            tagger.tagback_cooldown = tagger.tagback_cooldown_time
            runner.vel_x = 0
            runner.vel_y = 0
            runner.stun_timer = 10
            
            # Camera sequence on tag
            self.camera.clear_queue()
            self.camera.add_action("shake", 14)

    def draw(self, screen):
        if self.paused:
            self._draw_pause(screen)
            return

        # Draw world to a temp surface
        world_surface = pygame.Surface((screen.get_width(), screen.get_height()))
        world_surface.blit(self.app.background, (0, 0))
        self.app.renderer.draw(world_surface)
        self.app.level.draw(world_surface)
        for i, render in enumerate(self.app.player_renders):
            render.draw(world_surface, self.app.player_sims[i])

        # Apply camera transforms (shake, zoom) then blit to real screen
        screen.blit(self.camera.apply(world_surface), (0, 0))

    def _draw_pause(self, screen):
        # Defines a font and renders the pause text onto the screen
        font = pygame.font.SysFont(None, 48)
        # Font.render returns a new surface with the text drawn on it
        text = font.render("PAUSED  |  ESC = Resume  |  Q = Menu", True, (255, 255, 255))
        # Blit the text surface onto the main with pos 100, 100
        screen.blit(text, (100, 100))

