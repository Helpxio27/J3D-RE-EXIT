# game/systems/sound_system.py
import pygame
import os
from tools.path import resource_path

class SoundSystem:
    def __init__(self):
        pygame.mixer.init()
        self._sounds = {}
        self._music_volume = 0.4
        self._sfx_volume = 0.6

    # =====================
    # DOES: loads and caches a sound
    # =====================
    def load(self, key: str, path: str):
        full_path = resource_path(path)
        if os.path.exists(full_path):
            try:
                self._sounds[key] = pygame.mixer.Sound(full_path)
                self._sounds[key].set_volume(self._sfx_volume)
            except Exception as e:
                print(f"[SOUND] Failed to load {path}: {e}")
        else:
            print(f"[SOUND] File not found: {path}")

    # =====================
    # DOES: plays a sound by key
    # =====================
    def play(self, key: str):
        if key in self._sounds:
            self._sounds[key].play()

    # =====================
    # DOES: plays looping background music
    # =====================
    def play_music(self, path: str, loops=-1):
        full_path = resource_path(path)
        if os.path.exists(full_path):
            try:
                pygame.mixer.music.load(full_path)
                pygame.mixer.music.set_volume(self._music_volume)
                pygame.mixer.music.play(loops)
            except Exception as e:
                print(f"[SOUND] Music failed: {e}")

    def stop_music(self):
        pygame.mixer.music.stop()

    def set_sfx_volume(self, v: float):
        self._sfx_volume = v
        for s in self._sounds.values():
            s.set_volume(v)

    def set_music_volume(self, v: float):
        self._music_volume = v
        pygame.mixer.music.set_volume(v)

    def fade_out_music(self, duration_ms: int = 1500):
        """Fades out current music over duration in milliseconds"""
        pygame.mixer.music.fadeout(duration_ms)

    def play_music_after_fade(self, path: str, delay_ms: int = 1500):
        """Waits for fade out then plays new music"""
        import threading
        def _delayed_play():
            import time
            time.sleep(delay_ms / 1000.0)
            self.play_music(path)
        threading.Thread(target=_delayed_play, daemon=True).start()