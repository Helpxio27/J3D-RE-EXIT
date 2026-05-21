import pygame
import math
import random

class Camera:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        # Position
        self.x = 0.0
        self.y = 0.0
        self.target_x = 0.0
        self.target_y = 0.0

        # Zoom
        self.zoom = 1.0
        self.target_zoom = 1.0
        self.zoom_speed = 0.05

        # Shake
        self._shake_intensity = 0.0
        self._shake_decay = 0.85
        self._shake_offset_x = 0.0
        self._shake_offset_y = 0.0

        # Pan speed
        self.pan_speed = 0.08

        # =====================
        # CAMERA QUEUE SYSTEM
        # =====================
        self.queue = []
        self.current_action = None
        self.action_timer = 0.0

    # =====================
    # BASIC ACTION API
    # =====================

    def shake(self, intensity):
        self._shake_intensity = intensity

    def pan_to(self, x, y, speed=None):
        self.target_x = x - self.width / 2
        self.target_y = y - self.height / 2
        if speed is not None:
            self.pan_speed = speed

    def zoom_to(self, target_zoom, speed=None):
        self.target_zoom = target_zoom
        if speed is not None:
            self.zoom_speed = speed

    # =====================
    # QUEUE SYSTEM API
    # =====================

    def add_action(self, action_type, *args):
        """
        Example:
        camera.add_action("zoom", 1.2, 0.1)
        camera.add_action("wait", 0.5)
        camera.add_action("shake", 12)
        """
        self.queue.append((action_type, args))

    def clear_queue(self):
        self.queue.clear()
        self.current_action = None
        self.action_timer = 0.0

    # =====================
    # RESET
    # =====================

    def reset(self):
        self.x = 0.0
        self.y = 0.0
        self.target_x = 0.0
        self.target_y = 0.0
        self.zoom = 1.0
        self.target_zoom = 1.0
        self._shake_intensity = 0.0

        self.clear_queue()

    # =====================
    # UPDATE (includes queue processing)
    # =====================

    def update(self, dt=1.0):

        # ---------------------
        # PROCESS CAMERA QUEUE
        # ---------------------
        if self.current_action is None and self.queue:
            self.current_action = self.queue.pop(0)
            self.action_timer = 0.0

        if self.current_action is not None:
            action, args = self.current_action

            # WAIT ACTION
            if action == "wait":
                duration = args[0]
                self.action_timer += dt

                if self.action_timer >= duration:
                    self.current_action = None

            # ZOOM ACTION
            elif action == "zoom":
                target_zoom = args[0]
                speed = args[1] if len(args) > 1 else None

                self.zoom_to(target_zoom, speed)
                self.current_action = None

            # SHAKE ACTION
            elif action == "shake":
                intensity = args[0]

                self.shake(intensity)
                self.current_action = None

            # PAN ACTION
            elif action == "pan":
                x, y = args[0], args[1]
                speed = args[2] if len(args) > 2 else None

                self.pan_to(x, y, speed)
                self.current_action = None

        # ---------------------
        # SMOOTH CAMERA MOTION
        # ---------------------

        self.x += (self.target_x - self.x) * self.pan_speed
        self.y += (self.target_y - self.y) * self.pan_speed

        self.zoom += (self.target_zoom - self.zoom) * self.zoom_speed

        # ---------------------
        # SHAKE DECAY
        # ---------------------
        if self._shake_intensity > 0.1:
            self._shake_offset_x = random.uniform(-self._shake_intensity, self._shake_intensity)
            self._shake_offset_y = random.uniform(-self._shake_intensity, self._shake_intensity)
            self._shake_intensity *= self._shake_decay
        else:
            self._shake_intensity = 0.0
            self._shake_offset_x = 0.0
            self._shake_offset_y = 0.0

    # =====================
    # APPLY CAMERA EFFECTS
    # =====================

    def apply(self, surface):
        if self.zoom == 1.0 and self._shake_offset_x == 0 and self._shake_offset_y == 0:
            return surface
        zoomed_w = int(self.width * self.zoom)
        zoomed_h = int(self.height * self.zoom)
        zoomed = pygame.transform.scale(surface, (zoomed_w, zoomed_h))
        output = pygame.Surface((self.width, self.height))
        output.fill((0, 0, 0))
        blit_x = (self.width - zoomed_w) // 2 - int(self._shake_offset_x)
        blit_y = (self.height - zoomed_h) // 2 - int(self._shake_offset_y)
        output.blit(zoomed, (blit_x, blit_y))
        return output

    # =====================
    # WORLD TO SCREEN
    # =====================

    def world_to_screen(self, world_x, world_y):
        screen_x = (world_x - self.x) * self.zoom + self._shake_offset_x
        screen_y = (world_y - self.y) * self.zoom + self._shake_offset_y
        return int(screen_x), int(screen_y)