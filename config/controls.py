# config/controls.py
import pygame

CONTROLS = [
    {
        "left":      pygame.K_s,
        "right":     pygame.K_f,
        "jump":      pygame.K_e,
        "drop":      pygame.K_d,
        "use_power": pygame.K_d,      # ← same as drop for P1
    },
    {
        "left":      pygame.K_LEFT,
        "right":     pygame.K_RIGHT,
        "jump":      pygame.K_UP,
        "drop":      pygame.K_DOWN,
        "use_power": pygame.K_DOWN,   # ← same as drop for P2
    }
]