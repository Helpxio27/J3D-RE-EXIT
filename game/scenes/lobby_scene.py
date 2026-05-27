# game/scenes/lobby_scene.py
import pygame
from game.scenes.base_scene import BaseScene
from game.ui.widgets import Label, Button, Logo
from game.ui.theme import THEME
from game.world.camera import Camera
from network.client.client import GameClient
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT


class LobbyScene(BaseScene):
    def __init__(self, app):
        self.app = app
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Room code the player is typing
        self.code_input = ""
        self.max_code_length = 4

        # State: "ENTER_CODE", "WAITING", "ERROR"
        self.state = "ENTER_CODE"
        self.error_msg = ""

        # Widgets
        self.logo = Logo()
        self.logo.animate_in()

        self.prompt = Label("ENTER ROOM CODE", font_key="font_subtitle", color_key="secondary")
        self.prompt.fade_in()

        self.code_display = Label("____", font_key="font_title", color_key="accent")
        self.code_display.fade_in()

        self.hint = Label("Type a 4-letter code   ENTER to join   ESC to go back",
                          font_key="font_small", color_key="secondary")
        self.hint.fade_in()

        self.waiting_label = Label("Waiting for other player...",
                                   font_key="font_ui", color_key="secondary")

        self.error_label = Label("", font_key="font_small", color_key="danger")

        # Client — created fresh for each lobby attempt
        self.client = None

        # Dots animation for waiting screen
        self._dot_timer = 0.0
        self._dot_count = 0

        self.hint = Label("Type a 4-letter code   ENTER to join   ESC to go back   OOOO = Local play",
                  font_key="font_small", color_key="secondary")
        self.online_notice = Label(
            "/ ★ \ Online matches use a random map",
            font_key="font_small",
            color_key="secondary"
        )
        self.online_notice.fade_in()
    # =====================
    # EVENTS
    # =====================
    def handle_events(self, event):
        if self.state == "ENTER_CODE":
            self._handle_enter_code(event)
        elif self.state == "WAITING":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._back()

    def _handle_enter_code(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._back()

            elif event.key == pygame.K_BACKSPACE:
                self.code_input = self.code_input[:-1]
                self._update_code_display()
                self.camera.shake(2)

            elif event.key == pygame.K_RETURN:
                if len(self.code_input) == self.max_code_length:
                    self._attempt_join()
                else:
                    self.camera.shake(8)
                    self._show_error("Code must be 4 letters")

            elif event.unicode.isalpha() and len(self.code_input) < self.max_code_length:
                self.code_input += event.unicode.upper()
                self._update_code_display()
                self.camera.shake(2)

    def _update_code_display(self):
        display = self.code_input + "_" * (self.max_code_length - len(self.code_input))
        self.code_display.text = display

    def _attempt_join(self):
        # Create client and send join
        self.client = GameClient()
        self.client.join(self.code_input)
        self.app.client = self.client  # give app access to client
        self.state = "WAITING"
        self.camera.add_action("zoom", 1.05, 0.08)

    def _show_error(self, msg):
        self.error_msg = msg
        self.error_label.text = msg
        self.state = "ERROR"

    def _back(self):
        if self.client:
            self.client.disconnect()
        from game.scenes.menu_scene import MenuScene
        self.app.replace_scene(MenuScene(self.app))

    # =====================
    # UPDATE
    # =====================
    def update(self, accumulator):
        dt = self.app.render_dt
        self.camera.update(dt)
        self.logo.update()
        self.prompt.update()
        self.code_display.update()
        self.hint.update()
        self.online_notice.update()

        # Dots animation
        self._dot_timer += dt
        if self._dot_timer > 0.4:
            self._dot_timer = 0.0
            self._dot_count = (self._dot_count + 1) % 4

        if self.state == "WAITING" and self.client:
            self._check_server_response()

        # Reset error state after a moment
        if self.state == "ERROR":
            self._error_timer = getattr(self, "_error_timer", 0) + dt
            if self._error_timer > 2.0:
                self._error_timer = 0.0
                self.state = "ENTER_CODE"

        return accumulator
    
    def _check_server_response(self):
        messages = self.client.receive()
        for msg in messages:
            if msg.get("type") == "state":
                map_idx = msg.get("map_idx", 0) 
                self.app.online = True
                self._do_start_game(map_idx)
                return
            if msg.get("type") == "event" and msg.get("event") == "match_start":
                map_idx = msg["data"].get("map_idx", 0)
                self.app.online = True
                self._do_start_game(map_idx)
                return

        if self.client.error:
            self._show_error(self.client.error)
            self.client.error = None
            self.state = "ERROR"

    def _do_start_game(self, map_idx):
        self.camera.add_action("shake", 8)
        self.camera.add_action("zoom", 1.1, 0.15)
        self.camera.add_action("wait", 0.3)
        self.app.start_game(map_idx)

    def _attempt_join(self):
        print(f"[LOBBY] _attempt_join called, code='{self.code_input}'")
        if self.code_input == "OOOO":
            # Local play | skip network, go straight to map select
            self.app.online = False
            self.app.client = None
            from game.scenes.menu_scene import MenuScene
            scene = MenuScene(self.app)
            scene._transition_to("MAP_SELECT")
            scene._apply_state("MAP_SELECT")
            self.app.replace_scene(scene)
            return

        # Online play
        self.client = GameClient()
        self.client.join(self.code_input)
        self.app.client = self.client
        self.state = "WAITING"
        self.camera.add_action("zoom", 1.05, 0.08)

    def _start_game(self):
        self.app.online = True
        print(f"[CLIENT] Starting game online={self.app.online} client={self.app.client} connected={self.app.client.connected}")
        self.camera.add_action("shake", 8)
        self.camera.add_action("zoom", 1.1, 0.15)
        self.camera.add_action("wait", 0.3)
        self.app.start_game(0)

    # =====================
    # DRAW
    # =====================
    def draw(self, screen):
        screen.fill(THEME["background"])

        self.logo.draw(screen, SCREEN_WIDTH // 2, 80, anchor="midtop")

        if self.state == "ENTER_CODE" or self.state == "ERROR":
            self._draw_enter_code(screen)
        elif self.state == "WAITING":
            self._draw_waiting(screen)

        self.hint.draw(screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50, anchor="midbottom")

        result = self.camera.apply(screen)
        if result is not screen:
            screen.blit(result, (0, 0))

    def _draw_enter_code(self, screen):
        self.prompt.draw(screen, SCREEN_WIDTH // 2, 260, anchor="midtop")
        self.code_display.draw(screen, SCREEN_WIDTH // 2, 340, anchor="midtop")
        self.online_notice.draw(screen, SCREEN_WIDTH // 2, 460, anchor="midtop")

        if self.state == "ERROR":
            self.error_label.draw(screen, SCREEN_WIDTH // 2, 510, anchor="midtop")

    def _draw_waiting(self, screen):
        dots = "." * self._dot_count
        self.waiting_label.text = f"Waiting for other player{dots}"
        self.waiting_label.draw(screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, anchor="center")

        code_label = Label(f"Room: {self.code_input}",
                           font_key="font_subtitle", color_key="accent")
        code_label.alpha = 255
        code_label.draw(screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80, anchor="midtop")