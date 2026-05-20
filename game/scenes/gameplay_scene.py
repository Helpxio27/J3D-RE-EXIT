# game/scenes/gameplay_scene.py
import pygame
from game.scenes.base_scene import BaseScene
from game.world.collision import circle_rect_collision
from config.settings import FIXED_DT

class GameplayScene(BaseScene):
    def __init__(self, app):
        self.app = app
        self.paused = False  

    # =====================
    # DECIDES: gameplay input pause, quit to menu
    # =====================
    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.paused = not getattr(self, 'paused', False)
            if getattr(self, 'paused', False) and event.key == pygame.K_q:
                self.app.reset_to_menu()
                
            # “Look inside SELF for an attribute called "paused".”
            # If it exists → return it
            # If it doesn’t → return False

    # =====================
    # DOES: advances the match by dt seconds
    # =====================
    def update(self, accumulator):
        if getattr(self, 'paused', False):
            return accumulator  # ← return it unchanged

        inputs = self.app._build_inputs()

        if self.app.online:
            self.app._send_network_input(inputs[0])

        while accumulator >= FIXED_DT:
            self._tick(inputs)
            accumulator -= FIXED_DT

        return accumulator  # ← return the remainder

    def _tick(self, inputs):
        # Move players
        for i, sim in enumerate(self.app.player_sims):
            inp = inputs[i] if i < len(inputs) else {}
            sim.update(self.app.level.walls, inp)

        # Update renders
        for i, render in enumerate(self.app.player_renders):
            render.update(self.app.render_dt, self.app.player_sims[i])

        # Tag logic
        self._update_tag()

    # =====================
    # DECIDES: should a tag happen? DOES: applies it
    # =====================
    def _update_tag(self):
        tagger = next((p for p in self.app.player_sims if p.is_tagger), None)
        runner = next((p for p in self.app.player_sims if not p.is_tagger), None)

        # Equivalent to: if tagger and runner and tagger.can_tag(runner):
        # tagger = None
        # for p in self.app.player_sims:
        #     if p.is_tagger:
        #         tagger = p
        #         break

        if tagger and runner and tagger.can_tag(runner):
            tagger.is_tagger = False
            runner.is_tagger = True
            tagger.tagback_cooldown = tagger.tagback_cooldown_time
            runner.vel_x = 0
            runner.vel_y = 0
            runner.stun_timer = 10

    # =====================
    # DOES: draws the match, or pause overlay
    # =====================
    def draw(self, screen):
        if getattr(self, 'paused', False):
            self._draw_pause(screen)
            return

        screen.blit(self.app.background, (0, 0))
        self.app.renderer.draw(screen)
        self.app.level.draw(screen)
        for i, render in enumerate(self.app.player_renders):
            render.draw(screen, self.app.player_sims[i])

    def _draw_pause(self, screen):
        font = pygame.font.SysFont(None, 48)
        text = font.render("PAUSED  |  ESC = Resume  |  Q = Menu", True, (255, 255, 255))
        screen.blit(text, (100, 100))