# config/controls.py
import pygame

CONTROLS = [
    {
        "left":      pygame.K_a,
        "right":     pygame.K_d,
        "jump":      pygame.K_w,
        "drop":      pygame.K_s,
        "use_power": pygame.K_s,      # ← same as drop for P1
    },
    {
        "left":      pygame.K_LEFT,
        "right":     pygame.K_RIGHT,
        "jump":      pygame.K_UP,
        "drop":      pygame.K_DOWN,
        "use_power": pygame.K_DOWN,   # ← same as drop for P2
    }
]